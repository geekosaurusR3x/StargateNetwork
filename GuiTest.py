#!/usr/bin/env python3
import StargateNetwork.helpers as StargateNetworkUtils
import tkinter as tk
import pyglet
import os


class GUI(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        pyglet.font.add_file('font/Stargate SG1 Address Glyphs.ttf')

        self.IpInput = tk.Entry(self, bd=5)
        self.IpInput.pack()

        self.submitButton = tk.Button(
            self, command=self.buttonClick, text="Validate")

        self.submitButton.pack()
        self.StargateSymbols = tk.Label(self, text="", font=(
            'Stargate SG1 Address Glyphs', 25))

        self.StargateSymbols.pack()

    def buttonClick(self):
        Ip = StargateNetworkUtils.SequenceToListInt(self.IpInput.get())
        StargateAdress = StargateNetworkUtils.IpToStargateCode(Ip)
        IPDecode = StargateNetworkUtils.StargateCodeToIp(StargateAdress)
        text = self.ListStargateToSequence(StargateAdress)
        self.StargateSymbols.configure(text=text)
        print(f'{Ip} -> {StargateAdress}')
        print(f'{StargateAdress} -> {IPDecode}')
        print(text)

    def ListStargateToSequence(self, l):
        return ''.join(self.StargateSymbolToChar(s) for s in l)

    def StargateSymbolToChar(self, num):
        i = 0
        map = {}
        for c in range(42, 42+23):
            map[i] = chr(c)
            i += 1
        for c in range(61, 61+15):
            map[i] = chr(c)
            i += 1
        map[39] = 'A'
        return chr(42+num)


if __name__ == "__main__":
    root = tk.Tk()
    app = GUI(master=root)
    app.mainloop()
