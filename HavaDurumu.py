import sqlite3
import http.client
from urllib.parse import quote
from tkinter import *
from tkinter import messagebox, TclError
import json
import matplotlib.pyplot as plt

# try except bloklarını aidan aldım 


def veritabani():
    dosya = sqlite3.connect("hava_durumu.db")
    cur = dosya.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS HavaDurumu (sehir , tarih , gun , durum , derece REAL)")
    dosya.commit()
    dosya.close()

veritabani()

def veriEkle(sehir, veri):
    dosya = sqlite3.connect("hava_durumu.db")
    cur = dosya.cursor()
    cur.execute("DELETE FROM HavaDurumu WHERE sehir = ?", (sehir,))
    for v in veri:
        try:
            derece = float(v['degree'])
        except ValueError:
            derece = 0.0
        cur.execute("INSERT INTO HavaDurumu (sehir, tarih, gun, durum, derece) VALUES (?, ?, ?, ?, ?)",
                    (sehir, v['date'], v['day'], v['description'], derece))
    dosya.commit()
    dosya.close()

pen = Tk()
pen.title('Hava Durumu')


# projeyi kütüphane internetiyle yapıyordum okul interneti colletapiyi engelliyormus bunu sonradan 
# farkettim oy yüzden sorgu fonkisyonunun yarısından fazasını ai a düzelttirdim 

def sorgu(sehir):
    conn = http.client.HTTPSConnection("api.collectapi.com")
    path = f"/weather/getWeather?data.lang=tr&data.city={quote(sehir)}"
    headers = {
        'content-type': "application/json",
        'authorization': "apikey 6xB0L9XYwMKRnV2ii8kZI5:70jV3bN0Q6hcRLtMMMchZi"
    }
    try:
        conn.request("GET", path, headers=headers)
        res = conn.getresponse()
        data = res.read()
        if res.status == 200:
            return json.loads(data.decode("utf-8"))
        else:
            return None
    except Exception as e:
        messagebox.showerror("Bağlantı Hatası", str(e))
        return None

def gunluk():
    try:
        secilen = lb.get(lb.curselection())
        hava_durumu = sorgu(secilen)
        if hava_durumu:
            derece = hava_durumu['result'][0]['degree']
            durum = hava_durumu['result'][0]['description']
            messagebox.showinfo("Hava Durumu", f"{secilen} için hava durumu:\nSıcaklık: {derece}°C\nDurum: {durum}")
        else:
            messagebox.showerror("Hata", "Hava durumu alınamadı.")
    except TclError:
        messagebox.showwarning("Uyarı", "Herhangi bir öğe seçilmedi.")


# grafik çiziminde aidan yardım aldım

def grafik(gun, derece, sehir):
    plt.figure(figsize=(8, 4))
    plt.plot(gun, derece, marker='o', linestyle='-', color='blue')
    plt.title(f"{sehir} - Haftalık Sıcaklık Grafiği")
    plt.xlabel("Tarih")
    plt.ylabel("Sıcaklık (°C)")
    plt.grid(True)
    plt.tight_layout()
    plt.xticks(rotation=45)
    plt.show()

def haftalik():
    try:
        secilen = lb.get(lb.curselection())
        hava_durumu = sorgu(secilen)
        if hava_durumu:
            veriEkle(secilen, hava_durumu["result"])
            dosya = sqlite3.connect("hava_durumu.db")
            cur = dosya.cursor()
            cur.execute("SELECT tarih, gun, durum, derece FROM HavaDurumu WHERE sehir = ?", (secilen,))
            veriAl = cur.fetchall()
            dosya.close()

            lb2.delete(0, END)
            tarihler = []
            sicakliklar = []
            for i in veriAl:
                lb2.insert(END, f"{i[0]} / {i[1]} / {i[2]} / {i[3]}°C")
                tarihler.append(i[0])
                sicakliklar.append(i[3])

            grafik(tarihler, sicakliklar, secilen)
        else:
            messagebox.showerror("Hata", "Hava durumu alınamadı.")
    except TclError:
        messagebox.showwarning("Uyarı", "Herhangi bir öğe seçilmedi.")


# şehirleri ai dan aldım
sehirler = [
    "Adana", "Adıyaman", "Afyonkarahisar", "Ağrı", "Aksaray", "Amasya", "Ankara", "Antalya",
    "Ardahan", "Artvin", "Aydın", "Balıkesir", "Bartın", "Batman", "Bayburt", "Bilecik",
    "Bingöl", "Bitlis", "Bolu", "Burdur", "Bursa", "Çanakkale", "Çankırı", "Çorum", "Denizli",
    "Diyarbakır", "Düzce", "Edirne", "Elazığ", "Erzincan", "Erzurum", "Eskişehir", "Gaziantep",
    "Giresun", "Gümüşhane", "Hakkari", "Hatay", "Iğdır", "Isparta", "İstanbul", "İzmir",
    "Kahramanmaraş", "Karabük", "Karaman", "Kars", "Kastamonu", "Kayseri", "Kilis", "Kırıkkale",
    "Kırklareli", "Kırşehir", "Kocaeli", "Konya", "Kütahya", "Malatya", "Manisa", "Mardin",
    "Mersin", "Muğla", "Muş", "Nevşehir", "Niğde", "Ordu", "Osmaniye", "Rize", "Sakarya",
    "Samsun", "Şanlıurfa", "Siirt", "Sinop", "Şırnak", "Sivas", "Tekirdağ", "Tokat", "Trabzon",
    "Tunceli", "Uşak", "Van", "Yalova", "Yozgat", "Zonguldak"
]


pen.geometry("700x300")
 


frame = Frame(pen, padx=10 , pady=10)
frame.grid(row=0, column=0, stick="ns")

lb = Listbox(frame, height=15, width=30)
lb.grid(row=0, column=0, rowspan=4, sticky="nsew")

scrollbar=Scrollbar(frame, orient=VERTICAL, command=lb.yview)
scrollbar.grid(row=0, column=1, rowspan=4, sticky="ns")

for sehir in sehirler:
    lb.insert(END, sehir)

btn = Button(frame, text='Anlık Hava Durumu', command=gunluk, bg="#ADD8E6")
btn.grid(row=4, column=0, pady=10)

frame2 = Frame(pen , padx=10, pady=10)
frame2.grid(row=0, column=1,sticky="n")

lb2 = Listbox(frame2, height=10, width=50)
lb2.grid(row=0, column=0, sticky="nsew")

btn2 = Button(frame2, text='Haftalık Hava Durumu ve Grafiği', command=haftalik, bg ="#ADD8E6")
btn2.grid(row=1, column=0, pady=10)

pen.mainloop()