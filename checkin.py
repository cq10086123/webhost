import os
import requests

def denglu():
    raw_accounts = os.environ.get("ACCOUNTS", "")
    print("ACCOUNTS =", os.getenv("ACCOUNTS"))
    account_entries = [entry.strip() for entry in raw_accounts.split(";") if entry.strip()]

    urls = []
    for i, entry in enumerate(account_entries, 1):
        try:
            email, passwd = entry.split(":")
            urls.append({
                "login_url": "https://ikuuu.one/auth/login",
                "checkin_url": "https://ikuuu.one/user/checkin",
                "credentials": {
                    "email": email,
                    "passwd": passwd
                },
                "account_name": f"Account {i}"
            })
        except ValueError:
            print(f"格式错误：{entry}，应为 email:password")

    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        'x-requested-with': "XMLHttpRequest"
    }

    results = {}
    for site in urls:
        try:
            payload = {
                'email': site['credentials']['email'],
                'passwd': site['credentials']['passwd'],
                'code': "",
                'remember_me': "on",
                'host': site['login_url'].split('/')[2]
            }
            with requests.Session() as session:
                login_response = session.post(site['login_url'], data=payload, headers=headers)
                login_response.raise_for_status()

                if login_response.json().get("msg") == "登录成功":
                    print(f"{site['account_name']} 登录成功")
                    cookie_str = "; ".join([f"{c.name}={c.value}" for c in session.cookies])
                    checkin_response = session.post(site['checkin_url'], headers=headers)
                    checkin_response.encoding = 'utf-8'
                    checkin_msg = checkin_response.json().get("msg", "无返回消息")
                    results[site['account_name']] = {
                        'url': site['login_url'],
                        'cookie': cookie_str,
                        'checkin_result': checkin_msg
                    }
                else:
                    print(f"{site['account_name']} 登录失败: {login_response.json().get('msg')}")
        except Exception as e:
            print(f"{site['account_name']} 操作失败: {e}")

    return results if results else None

if __name__ == "__main__":
    result = denglu()
    if result:
        for account, data in result.items():
            print(f"\n账户: {account}")
            print(f"URL: {data['url']}")
            print(f"签到结果: {data['checkin_result']}")
    else:
        print("所有账户操作失败")
