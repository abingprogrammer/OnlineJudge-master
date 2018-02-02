import xmlrpc.client#2018.1.26

if __name__ == "__main__":
    try:
        server = xmlrpc.client.Server("http://localhost:9005/RPC2")
        info = server.supervisor.getAllProcessInfo()
        error_states = list(filter(lambda x: x["state"] != 20, info))
        exit(len(error_states))
    except Exception as e:
        #print(e.with_traceback())
        print(e.with_traceback(tb='错误'))  # 2018.1.31
        exit(1)
