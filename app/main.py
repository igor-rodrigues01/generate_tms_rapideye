from threading import Thread


class Perform(Thread):

    def __init__(self):
        super(Perform, self).__init__()

    def f1(self):
        s = []
        for i in range(50000):
            s.append(i)
            if i == 3000 - 1:
                print(s,'\n\n\n\n\n\n\n')

    def run(self):
        self.f1()

def f1(i):
    import pdb; pdb.set_trace()
    s = []
    for i in range(50000):
        s.append(i)
        if i == 3000 - 1:
            print(s,'\n\n\n\n\n\n\n')


t = Thread(target=f1, args=[id(t)], daemon=True)
t2 = Thread(target=f1, daemon=True)
t3 = Thread(target=f1, daemon=True)
t4 = Thread(target=f1, daemon=True)
t.start()
t2.start()
t3.start()
t4.start()

t.join()
t2.join()
t3.join()
t4.join()
