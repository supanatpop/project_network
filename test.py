import threading

def thread_function():
    while True:
        print('tt')

x = threading.Thread(target=thread_function)
x.start()