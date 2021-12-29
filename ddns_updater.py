import stun
import schedule
import requests
import json
import time
import argparse
import logging

parser = argparse.ArgumentParser(description="DDNS for reg.ru")
parser.add_argument("login", help="Почта на reg.ru")
parser.add_argument("password", help="Пароль на reg.ru")
parser.add_argument("-d", dest="delay", default=30, type=int,
                    help="Задержка между проверкой ip в минутах")

logging.basicConfig(filename="logs.txt",
                    format='[%(asctime)s] [%(levelname)s] - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S',
                    level=logging.INFO)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("pystun3").setLevel(logging.WARNING)

prev_ip = ""


def cheker():
    global prev_ip

    cur_ip = stun.get_ip_info()[1]
    logging.debug(cur_ip)

    if cur_ip != prev_ip:
        res = update_ip(cur_ip)
        if res is not True:
            code, message = res
            if code == "USER_AUTHENTICATION_FAILED":
                logging.error("Неверный логин или пароль")
            elif code == "ACCESS_DENIED_FROM_IP":
                logging.error("Диапазон ваших ip адресов не добавлен в список разрешенных")
            elif code == "INVALID_DOMAIN_NAME_FORMAT":
                logging.error("Один из указанных доменов не найден")
            else:
                logging.error("Неизвестная ошибка: %s", message)
        else:
            logging.info("IP был изменен")
            prev_ip = cur_ip


def update_ip(ip):
    with open("domains.txt") as file:
        for groups in file.read().split("\n\n"):
            domain_name, *aliases = groups.split("\n")
            if domain_name:
                domains = [{"dname": domain_name}]

                input_data = {"username": args.login,
                              "password": args.password,
                              "domains": domains,
                              "output_content_type":"json"}
                params = {"input_data": json.dumps(input_data), "input_format": "json"}

                res = requests.post("https://api.reg.ru/api/regru2/zone/get_resource_records",
                                    params=params).json()
                logging.debug(res)
                if res["result"] == "error":
                    return res["error_code"], res["error_text"]
                if res["answer"]["domains"][0]["result"] == "error":
                    return res["answer"]["domains"][0]["error_code"], res["answer"]["domains"][0]["error_text"]

                subs_to_clear = res["answer"]["domains"][0]["rrs"]

                for sub in subs_to_clear:
                    if sub["subname"] in aliases:
                        input_data = {"username": args.login,
                                      "password": args.password,
                                      "domains": domains,
                                      "subdomain": sub["subname"],
                                      "content": sub["content"],
                                      "record_type": "A",
                                      "output_content_type":"json"}
                        params = {"input_data": json.dumps(input_data), "input_format": "json"}
                        res = requests.post("https://api.reg.ru/api/regru2/zone/remove_record", params=params).json()
                        logging.debug(res)
                        if res["result"] == "error":
                            return res["error_code"], res["error_text"]

                for subdomain in aliases:
                    if subdomain:
                        input_data = {"username": args.login,
                                      "password": args.password,
                                      "domains": domains,
                                      "subdomain": subdomain,
                                      "ipaddr": ip,
                                      "output_content_type":"json"}
                        params = {"input_data": json.dumps(input_data), "input_format": "json"}
                        res = requests.post("https://api.reg.ru/api/regru2/zone/add_alias", params=params).json()
                        logging.debug(res)
                        if res["result"] == "error":
                            return res["error_code"], res["error_text"]

    return True


if __name__ == '__main__':
    args = parser.parse_args()

    schedule.every(args.delay).minutes.do(cheker)
    cheker()

    while True:
        schedule.run_pending()
        time.sleep(1)
