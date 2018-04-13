

class Battery:

    def __init__(self, SOC_init, dt, mode, capacity):
        self.SOC = SOC_init
        self.dt = dt
        self.mode = mode
        self.capacity = capacity
    def update_current(self, i0,i1):
        self.i0 = i0
        self.i1 = i1
        self.soc = self.soc_cc()
        return self.soc
    def soc_cc(self):

        if self.mode == 'C':
            if self.SOC != 100 and self.SOC < 100:
                self.SOC_current = self.SOC + abs(self.i1 - self.i0) * self.dt / self.capacity
            else:
                self.SOC_current = self.SOC
                print("Battery is fully charged")
        else:
            self.SOC_current = self.SOC - abs(self.i1 - self.i0) * self.dt / self.capacity
        return self.SOC_current


# if __name__ == '__main__':
#    B1 =  Battery(80,2,'C',60)
#    soc = B1.update_current(2,5)
#    print(soc)

