import sqlite3

# Veritabanı dosyasını oluştur (eğer yoksa)
conn = sqlite3.connect('okul_servis_sistemi2.db')
cursor = conn.cursor()

# Ogrenciler tablosunu oluştur
cursor.execute('''
CREATE TABLE IF NOT EXISTS Ogrenciler (
    ogrenciID TEXT PRIMARY KEY,
    sifre TEXT NOT NULL,
    email TEXT
);
''')
# Öğretmenler tablosunu oluştur
cursor.execute('''
CREATE TABLE IF NOT EXISTS Ogretmenler (
    ogretmenID TEXT PRIMARY KEY,
    sifre TEXT NOT NULL,
    email TEXT
);
''')

# Şoförler tablosunu oluştur
cursor.execute('''
CREATE TABLE IF NOT EXISTS Soforler (
    soforID TEXT PRIMARY KEY,
    sifre TEXT NOT NULL,
    email TEXT
);
''')

# Yöneticiler tablosunu oluştur
cursor.execute('''
CREATE TABLE IF NOT EXISTS Yoneticiler (
    yoneticiID TEXT PRIMARY KEY,
    sifre TEXT NOT NULL,
    email TEXT
);
''')
 # Ders Programı
cursor.execute('''
CREATE TABLE IF NOT EXISTS DersProgrami (
    dersID INTEGER PRIMARY KEY AUTOINCREMENT,
    gun TEXT NOT NULL,
    saat TEXT NOT NULL,
    ders_adi TEXT NOT NULL
);
''')
# Katılım Durumu
cursor.execute('''
CREATE TABLE IF NOT EXISTS KatilimDurumu (
    ogrenciID TEXT NOT NULL,
    dersID INTEGER NOT NULL,
    katilim TEXT NOT NULL CHECK (katilim IN ('katil', 'katilmiyorum')), -- Katılım durumu kontrolü
    PRIMARY KEY (ogrenciID, dersID), -- ogrenciID ve dersID birincil anahtar
    FOREIGN KEY (ogrenciID) REFERENCES Ogrenciler (ogrenciID),
    FOREIGN KEY (dersID) REFERENCES DersProgrami (dersID)
);
 ''')

# Veritabanı değişikliklerini kaydet
conn.commit()

# Bağlantıyı kapat
conn.close()

print("Veritabanı ve tablo başarıyla oluşturuldu!")
