from flask import Flask, render_template, request, redirect, url_for
from models import get_db_connection, Ogrenci, Ogretmen, Yonetici, Sofor
import sqlite3

app = Flask(__name__)

# Ana Sayfa
@app.route('/')
def index():
    return render_template('anasayfa.html')

# Öğrenci Giriş
@app.route('/Giris/ogrenci_giris', methods=['GET', 'POST'])
def ogrenci_giris():
    error = None  # Hata mesajı için bir değişken
    if request.method == 'POST':
        ogrenciID = request.form['ogrenciID']
        sifre = request.form['sifre']
        
        try:
            conn = get_db_connection()
            ogrenci = Ogrenci.giris(conn, ogrenciID, sifre)
            
            if ogrenci:
                return redirect(url_for('ogrenci_islem'))  # Başarılı girişte öğrenci işlem paneline yönlendir
            else:
                error = "Geçersiz kullanıcı adı veya şifre."  # Hata mesajı
        finally:
            conn.close()

    return render_template('Giris/ogrenci_giris.html', error=error)

# Öğrenci Kayıt
@app.route('/Kayit/ogrenci_kayit', methods=['GET', 'POST'])
def ogrenci_kayit():
    if request.method == 'POST':
        ogrenciID = request.form['ogrenciID']
        sifre = request.form['sifre']
        email = request.form['email']
        
        try:
            conn = get_db_connection()
            ogrenci = Ogrenci(ogrenciID, sifre, email)
            ogrenci.kayit(conn)
            return redirect(url_for('index'))  # Kayıttan sonra ana sayfaya yönlendir
        except sqlite3.IntegrityError:
            return "Bu Öğrenci ID zaten kayıtlı!", 400  # Hata durumunda mesaj döndür
        finally:
            conn.close()
    
    return render_template('Kayit/ogrenci_kayit.html')

# Öğrenci İşlem Sayfası
@app.route('/Islemler/ogrenci_islem', methods=['GET', 'POST'])
def ogrenci_islem():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Ders programını veritabanından al
        cursor.execute("SELECT * FROM DersProgrami")
        ders_programi = cursor.fetchall()

        if request.method=='POST':
            action = request.form.get('action')  # Hangi işlem yapılacak ('katil', 'katilmiyorum')
            ders_id = request.form.get('dersID')
            ogrenciID = request.form.get('ogrenciID')

            if action == 'katil' or 'katilmiyorum':
                try: 
                    cursor.execute('''
                        INSERT INTO KatilimDurumu (ogrenciID, dersID, katilim)
                        VALUES (?, ?, ?)
                        ON CONFLICT(ogrenciID, dersID) DO UPDATE SET katilim = excluded.katilim;
                    ''', (ogrenciID, ders_id, action))
                    conn.commit()
                except sqlite3.IntegrityError:
                    return "Katılım durumu eklenirken bir hata oluştu.", 400
                return redirect(url_for('ogrenci_islem'))  # Sayfayı yenilemek için


        return render_template('Islemler/ogrenci_islem.html', ders_programi=ders_programi)
    except Exception as e:
        return f"Hata oluştu: {e}"
    finally:
        conn.close()

# Öğretmen Giriş
@app.route('/Giris/ogretmen_giris', methods=['GET', 'POST'])
def ogretmen_giris():
    error = None  # Hata mesajı için bir değişken
    if request.method == 'POST':
        ogretmenID = request.form['ogretmenID']
        sifre = request.form['sifre']
        
        try:
            conn = get_db_connection()
            ogretmen = Ogretmen.giris(conn, ogretmenID, sifre)
            
            if ogretmen:
                return redirect(url_for('ogretmen_islem'))  # Başarılı girişte öğretmen işlem paneline yönlendir
            else:
                error = "Geçersiz kullanıcı adı veya şifre."  # Hata mesajı
        finally:
            conn.close()

    return render_template('Giris/ogretmen_giris.html', error=error)

# Öğretmen Kayıt
@app.route('/Kayit/ogretmen_kayit', methods=['GET', 'POST'])
def ogretmen_kayit():
    if request.method == 'POST':
        ogretmenID = request.form['ogretmenID']
        sifre = request.form['sifre']
        email = request.form['email']
        
        try:
            conn = get_db_connection()
            ogretmen = Ogretmen(ogretmenID, sifre, email)
            ogretmen.kayit(conn)
            return redirect(url_for('index'))  # Kayıttan sonra ana sayfaya yönlendir
        except sqlite3.IntegrityError:
            return "Bu Öğretmen ID zaten kayıtlı!", 400  # Hata durumunda mesaj döndür
        finally:
            conn.close()
    
    return render_template('Kayit/ogretmen_kayit.html')

# Öğretmen İşlem Sayfası
@app.route('/Islemler/ogretmen_islem', methods=['GET', 'POST'])
def ogretmen_islem():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Ders programını veritabanından al
        cursor.execute("SELECT * FROM DersProgrami")
        ders_programi = cursor.fetchall()

        if request.method == 'POST':
            action = request.form.get('action')  # Hangi işlem yapılacak ('add', 'update', 'delete')
            ders_id = request.form.get('dersID')
            gun = request.form.get('gun')
            saat = request.form.get('saat')
            ders_adi = request.form.get('ders_adi')

            if action == 'add':  # Yeni ders ekleme
                try:
                    cursor.execute("""
                        INSERT INTO DersProgrami (gun, saat, ders_adi) 
                        VALUES (?, ?, ?)
                    """, (gun, saat, ders_adi))
                    conn.commit()
                except sqlite3.IntegrityError:
                    return "Ders eklenirken bir hata oluştu.", 400

            elif action == 'update' and ders_id:  # Ders güncelleme
                cursor.execute("""
                    UPDATE DersProgrami 
                    SET gun = ?, saat = ?, ders_adi = ? 
                    WHERE dersID = ?
                """, (gun, saat, ders_adi, ders_id))
                conn.commit()

            elif action == 'delete' and ders_id:  # Ders silme
                cursor.execute("DELETE FROM DersProgrami WHERE dersID = ? ", (ders_id,))
                conn.commit()

            return redirect(url_for('ogretmen_islem'))  # Sayfayı yenilemek için

        return render_template('Islemler/ogretmen_islem.html', ders_programi=ders_programi)

    except Exception as e:
        return f"Hata oluştu: {e}"
    finally:
        conn.close()

# Yönetici Giriş
@app.route('/Giris/yonetici_giris', methods=['GET', 'POST'])
def yonetici_giris():
    error = None  # Hata mesajı için bir değişken
    if request.method == 'POST':
        yoneticiID = request.form['yoneticiID']
        sifre = request.form['sifre']
        
        try:
            conn = get_db_connection()
            yonetici = Yonetici.giris(conn, yoneticiID, sifre)
            
            if yonetici:
                return redirect(url_for('yonetici_islem'))  # Başarılı girişte yönetici işlem paneline yönlendir
            else:
                error = "Geçersiz kullanıcı adı veya şifre."  # Hata mesajı
        finally:
            conn.close()

    return render_template('Giris/yonetici_giris.html', error=error)

# Yönetici Kayıt
@app.route('/Kayit/yonetici_kayit', methods=['GET', 'POST'])
def yonetici_kayit():
    if request.method == 'POST':
        yoneticiID = request.form['yoneticiID']
        sifre = request.form['sifre']
        email = request.form['email']
        
        try:
            conn = get_db_connection()
            yonetici = Yonetici(yoneticiID, sifre, email)
            yonetici.kayit(conn)
            return redirect(url_for('index'))  # Kayıttan sonra ana sayfaya yönlendir
        except sqlite3.IntegrityError:
            return "Bu yönetici ID zaten kayıtlı!", 400  # Hata durumunda mesaj döndür
        finally:
            conn.close()
    
    return render_template('Kayit/yonetici_kayit.html')

# Yönetici İşlem Sayfası
@app.route('/Islemler/yonetici_islem', methods=['GET'])
def yonetici_islem():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Saat bazında katılım durumunu sorgula
        cursor.execute('''
            SELECT
                dp.saat, 
                COUNT(kd.ogrenciID) AS katilan_ogrenci
            FROM KatilimDurumu kd
            JOIN DersProgrami dp ON kd.dersID = dp.dersID
            WHERE kd.katilim = 'katil'
            GROUP BY dp.saat
            ORDER BY dp.saat;
        ''')
        katilim_durumlari = cursor.fetchall()

        # Otobüs başına öğrenci kapasitesi
        otobus_kapasitesi = 20

        # Saat bazında otobüs sayısını ve boş otobüs sayısını hesapla
        otobus_sayilari = []
        for katilim in katilim_durumlari:
            saat = katilim[0]
            katilan_ogrenci = katilim[1]
            # Otobüs sayısını hesapla
            otobus_sayisi = (katilan_ogrenci + otobus_kapasitesi - 1) // otobus_kapasitesi  # Yuvarlama
            # Boş otobüs sayısını hesapla (otobüs kapasitesi - katılan öğrenci sayısı)
            bos_otobus_sayisi = max(0, otobus_sayisi - (katilan_ogrenci // otobus_kapasitesi))
            otobus_sayilari.append({
                'saat': saat,
                'katilan_ogrenci': katilan_ogrenci,
                'otobus_sayisi': otobus_sayisi,
                'bos_otobus_sayisi': bos_otobus_sayisi
            })

        return render_template('Islemler/yonetici_islem.html', otobus_sayilari=otobus_sayilari)

    except Exception as e:
        return f"Hata oluştu: {e}"

    finally:
        conn.close()

# Şoför Giriş
@app.route('/Giris/sofor_giris', methods=['GET', 'POST'])
def sofor_giris():
    error = None  # Hata mesajı için bir değişken
    if request.method == 'POST':
        soforID = request.form['soforID']
        sifre = request.form['sifre']
        
        try:
            conn = get_db_connection()
            sofor = Sofor.giris(conn, soforID, sifre)
            
            if sofor:
                return redirect(url_for('sofor_islem'))  # Başarılı girişte şoför işlem paneline yönlendir
            else:
                error = "Geçersiz kullanıcı adı veya şifre."  # Hata mesajı
        finally:
            conn.close()

    return render_template('Giris/sofor_giris.html', error=error)

# Şoför Kayıt
@app.route('/Kayit/sofor_kayit', methods=['GET', 'POST'])
def sofor_kayit():
    if request.method == 'POST':
        soforID = request.form['soforID']
        sifre = request.form['sifre']
        email = request.form['email']
        
        try:
            conn = get_db_connection()
            sofor = Sofor(soforID, sifre, email)
            sofor.kayit(conn)
            return redirect(url_for('index'))  # Kayıttan sonra ana sayfaya yönlendir
        except sqlite3.IntegrityError:
            return "Bu Şoför ID zaten kayıtlı!", 400  # Hata durumunda mesaj döndür
        finally:
            conn.close()
    
    return render_template('Kayit/sofor_kayit.html')

# Şoför İşlem Sayfası
@app.route('/Islemler/sofor_islem')
def sofor_islem():
    return render_template('Islemler/sofor_islem.html')

if __name__ == '__main__':
    app.run(debug=True) 