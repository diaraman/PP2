import json

def main():
    #Converting JSON to Python dictionary
    with open("/Users/bagitovberik/Desktop/pp2/practice04/exercises/json/sample-data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    #creating a table
    print("Interface Status")
    print("=" * 80)
    print(f"{'DN':50} {'Description':20} {'Speed':6} {'MTU':5}")
    print(f"{'-'*50} {'-'*20}  {'-'*6}  {'-'*5}")

    #Getting data from dictionary
    for item in data.get("imdata", []):
        attrs = item["l1PhysIf"]["attributes"]

        dn = attrs.get("dn", "")
        descr = attrs.get("descr", "")
        speed = attrs.get("speed", "")
        mtu = attrs.get("mtu", "")

        #Outputing in neccessary order
        print(f"{dn:50} {descr:20}  {speed:6}  {mtu:5}")

main()