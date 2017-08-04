#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
#Busqueda en pagina web
#-----------------------

#Inclusion de librerias necesarias
import sys
import mechanize
from bs4 import BeautifulSoup
import re
import encodings
import pypyodbc
from datetime import date, timedelta, datetime
#import sys 
#reload(sys) 
#sys.setdefaultencoding("utf-8")

def fechaahora():
    ahora = datetime.now()
    #print ahora
    YY = ahora.year
    mm = ahora.month
    dd = ahora.day
    hh = ahora.hour
    m = ahora.minute
    ss = ahora.second
    fech = str(mm)+'/'+str(dd)+'/'+str(YY)+' '+str(hh)+':'+str(m)+':'+str(ss)
    return fech

def fechainicio(idconsul, cursor):
    sqlf="SELECT MAX(FECHAF) FROM SCR_ANUNCIANTES WHERE ID_CONSULTA=?"
    valor=[idconsul]
    cursor.execute(sqlf, valor)
    resulf= cursor.fetchone()
    fechf = resulf[0]
    return fechf
#crear browser
br = mechanize.Browser()

#Busqueda de robots negativa
br.set_handle_equiv(False)
#br.set_handle_gzip(True)
#br.set_handle_redirect(True)
#br.set_handle_referer(True)
br.set_handle_robots(False)

br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

# Simula ser una persona
#br.addheaders = [('User-agent', 'Mozilla/5.0')] 
#br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')] 
br.addheaders = [('User-agent', 'Opera/9.25 (Macintosh; PPC Mac OS X; U; en)')]

#Conexion a la base de Datos
cnn = pypyodbc.connect(driver='{SQL Server}',server='66.232.22.196', database='foxclea_tareas', UID='FOXCLEA_TAREAS', PWD='JACINTO2014')

cursor = cnn.cursor()

sqlcmd = ("SELECT * FROM SCR_CONSULTAS WHERE ID_PORTAL = 2 AND ESTADO = 1")
#valor = [1]
#cursor.execute(sqlcmd, valor)
cursor.execute(sqlcmd)
resultado = cursor.fetchall()
for c in resultado:
    
    idconsulta = c[0]
    fecha_fincon= c[11]
    #print idconsulta
    #print fecha_prog
    maxpage = c[13]
    print "Conexion exitosa"

    fechahora = fechaahora()
    #print fechahora
    sqllog = ("INSERT INTO SCR_LOG (ID_CONSULTA, FECHA, MENSAJE, LINEA_COD, URL, DETALLE, TIPO) VALUES (?, ?, ?, ?, ?, ?, ?)")
    valor = [idconsulta, fechahora,'Conectando a la Base de Datos','40-50', 'https://wwww.booking.com', '', 1 ]
    cursor.execute(sqllog, valor)
    cursor.commit()

    #obtener la fecha del dia
    fecha = date.today()

    if fecha_fincon is None:
        fecha_fincon='0000-00-00'
    else:
        dias = fecha_fincon.date() - datetime.now().date()
        #print dias
    #print fecha_prog
    F =str(fecha_fincon).split(" ")
    #print F[0]
    #print Fecha
    #verificar la fecha programada
    if str(F[0]) != str(fecha):    
    
        #Llenar los campos de busqueda
        #print c[5]
        if c[5] is None:
            ss=str(c[4])
        else:
            ss= str(c[5]) + "%20de%20" + str(c[4])

        #str(result[3])
        #ss='Denia'
        fecha_inicio = fechainicio(idconsulta,cursor)
        #print fecha_inicio
        #print fecha
        if fecha_inicio is None:
            Fechadiv =str(fecha).split("-")
            #print Fechadiv
        else:
            Fech =str(fecha_inicio).split(" ")
            fecha = Fech[0]
            #print "fech %s" %fecha
            fecha = fecha_inicio.date()
            Fechadiv = str(Fech[0]).split("-")
            #print "fech %s" %fecha
        checkin_monthday=Fechadiv[2]
        #print checkin_monthday
        checkin_month=Fechadiv[1]
        checkin_year=Fechadiv[0]
        Fechasal = fecha + timedelta(days=c[10])
        Fechadiv2 =str(Fechasal).split("-")
        checkout_monthday=Fechadiv2[2]
        checkout_month=Fechadiv2[1]
        checkout_year=Fechadiv2[0]
        adultos = str(c[6])
        #

        print "Destino/Nombre Alojamiento: " + ss
        print "Fecha de Check-in: %s" % fecha
        print "Fecha de Check-out: %s" % Fechasal
        print "Adultos: %s" % adultos

        print "Cargando Datos...."
        #Actualizar la fecha programada de la consulta
        if fecha_inicio is None:
            sqllog = ("UPDATE SCR_CONSULTAS SET FECHA_PROGRA=? WHERE ID_CONSULTA=?")
            valor = [Fechasal, idconsulta]
            cursor.execute(sqllog, valor)
            cursor.commit()
        #Abrir Url
        url = u'https://www.booking.com'
        r = br.open(url)
        #Seleccionar el Formulario
        br.select_form(nr=0)

        #rellenar los campos
        br.form["ss"]=ss
        br.form["checkin_monthday"]=checkin_monthday
        br.form["checkin_month"]=checkin_month
        br.form["checkin_year"]=checkin_year
        br.form["checkout_monthday"]=checkout_monthday
        br.form["checkout_month"]=checkout_month
        br.form["checkout_year"]=checkout_year
        br.form["group_adults"]=[adultos]

        #enviar de Formulario
        data = br.submit()
    
        fechahora = fechaahora()
        sqllog = ("INSERT INTO SCR_LOG (ID_CONSULTA, FECHA, MENSAJE, LINEA_COD, URL, DETALLE, TIPO) VALUES (?, ?, ?, ?, ?, ?, ?)")
        valor = [idconsulta, fechahora,'Enviando formulario de busqueda a la pagina de Booking','82-104', 'https://wwww.booking.com', '', 1 ]
        cursor.execute(sqllog, valor)
        cursor.commit()
        print 'Enviando formulario de busqueda a la pagina de Booking'
        #Creacion de Instancia Soup de la pagina
        soup= BeautifulSoup(data,"html5lib")
        i = 0

        hrefaorder = "%s/searchresults.es.html?checkin_month=%s;checkin_monthday=%s;checkin_year=%s;checkout_month=%s;checkout_monthday=%s;checkout_year=%s;group_adults=%s;group_children=0;order=price;ss=%s;selected_currency=EUR;lang=es" % (url, checkin_month, checkin_monthday, checkin_year, checkout_month, checkout_monthday, checkout_year, adultos, ss)
        #print hrefaorder
        r = br.open(hrefaorder)
        #req = requests.get(hrefaorder)

        souporder = BeautifulSoup(r, "html5lib")

        fechahora = fechaahora()
        sqllog = ("INSERT INTO SCR_LOG (ID_CONSULTA, FECHA, MENSAJE, LINEA_COD, URL, DETALLE, TIPO) VALUES (?, ?, ?, ?, ?, ?, ?)")
        valor = [idconsulta, fechahora,'Cargando busqueda ordenada por precio','147-152', url, '', 1 ]
        cursor.execute(sqllog, valor)
        cursor.commit()
        print 'Cargando busqueda ordenada por precio'
        #print souporder
        #souporder.encode("utf-8")
        try:
            result = souporder.h1.string
            print result
            resul = re.findall('\\d+',result)
            i = 0
            totalhotel = 0
            text_total = None
            #---
            if(len(resul) == 2)
                text_total = resul[0] + resul[1]
            else:
                text_total = resul[0]
            #---           
            totalhotel = int(text_total)

            canthotel = 0

            #Obtener la cantidad de Paginas en la busqueda

            if maxpage is None:
                pagin = totalhotel/15
            else:
                pagin = maxpage
            if pagin <= 0:
                canthotel = 1
            else:
                canthotel = pagin
            canthotel = int(canthotel)

            #Ingresar a una lista los hoteles
            listhotl= []
            listhotlid = []
            sqlhotl = ("SELECT * FROM SCR_ANUNCIOS WHERE ID_PORTAL = 2")
            cursor.execute(sqlhotl)
            resulthotl = cursor.fetchall()
            for r in resulthotl:
                listhotl.append(r[1])
                listhotlid.append(r[0])
            #print listhotl

            fechahora = fechaahora()
            sqllog = ("INSERT INTO SCR_LOG (ID_CONSULTA, FECHA, MENSAJE, LINEA_COD, URL, DETALLE, TIPO) VALUES (?, ?, ?, ?, ?, ?, ?)")
            valor = [idconsulta, fechahora,'Obteniendo los anuncios de la SCR_ANUNCIOS','166-174', url, '', 1 ]
            cursor.execute(sqllog, valor)
            cursor.commit()

            #En este ciclo se obtiene el resultado de la busqueda 

            i=0
            rows = 15
            offset = 15
            m = 0
            #print "canthotel %d" %canthotel
            while i <= canthotel:
                #print "entre aqui"
                if i==0:
                    entradas = souporder.find_all('div', re.compile("sr_item sr_item_new sr_item_default sr_property_block"))
                    #print entradas
                    all_links = souporder.find('a', re.compile("paging-next ga_sr_gotopage"))
                    #print all_links
                    if all_links is None:
                        i = canthotel
                    else:
                        htmllink = hrefaorder = "%s/searchresults.es.html?checkin_month=%s;checkin_monthday=%s;checkin_year=%s;checkout_month=%s;checkout_monthday=%s;checkout_year=%s;group_adults=%s;group_children=0;order=price;ss=%s;rows=%s;offset=%s;selected_currency=EUR;lang=es" % (url, checkin_month, checkin_monthday, checkin_year, checkout_month, checkout_monthday, checkout_year, adultos, ss,rows, offset)
                        offset=offset + rows
                        #print htmllink
                    fechahora = fechaahora()
                    sqllog = ("INSERT INTO SCR_LOG (ID_CONSULTA, FECHA, MENSAJE, LINEA_COD, URL, DETALLE, TIPO) VALUES (?, ?, ?, ?, ?, ?, ?)")
                    valor = [idconsulta, fechahora,'Obteniendo el resultado de la busqueda en una pagina y el link de la pagina siguiente','192-201', url, '', 1 ]
                    cursor.execute(sqllog, valor)
                    cursor.commit()
                else:
                    r = br.open(htmllink)
                    html= BeautifulSoup(r,"html5lib")
                    #print html
                    entradas = html.find_all('div', re.compile("sr_item sr_item_new sr_item_default sr_property_block"))  
                    all_links = html.find('a', re.compile("paging-next ga_sr_gotopage"))
                    if all_links is None:
                        i = canthotel
                    else:
                        htmllink = hrefaorder = "%s/searchresults.es.html?checkin_month=%s;checkin_monthday=%s;checkin_year=%s;checkout_month=%s;checkout_monthday=%s;checkout_year=%s;group_adults=%s;group_children=0;order=price;ss=%s;rows=%s;offset=%s;selected_currency=EUR;lang=es" % (url, checkin_month, checkin_monthday, checkin_year, checkout_month, checkout_monthday, checkout_year, adultos, ss,rows, offset)
                        offset=offset + rows
                        #print htmllink
                    fechahora = fechaahora()
                    sqllog = ("INSERT INTO SCR_LOG (ID_CONSULTA, FECHA, MENSAJE, LINEA_COD, URL, DETALLE, TIPO) VALUES (?, ?, ?, ?, ?, ?, ?)")
                    valor = [idconsulta, fechahora,'Obteniendo el resultado de la busqueda en una pagina y el link de la pagina siguiente','209-218', url, '', 1 ]
                    cursor.execute(sqllog, valor)
                    cursor.commit()
        
                for k, entrada in enumerate(entradas):
                    #Ingresar a una lista los hoteles de competencia
                    listhotlcom= []
                    listhotlcomid= []
                    sqlhotl = ("SELECT * FROM SCR_COMPETENCIA WHERE ID_PORTAL = 2")
                    cursor.execute(sqlhotl)
                    resulthotl = cursor.fetchall()
                    for r in resulthotl:
                        listhotlcom.append(r[1])
                        listhotlcomid.append(r[0])
                    #print listhotlcom

                    fechahora = fechaahora()
                    sqllog = ("INSERT INTO SCR_LOG (ID_CONSULTA, FECHA, MENSAJE, LINEA_COD, URL, DETALLE, TIPO) VALUES (?, ?, ?, ?, ?, ?, ?)")
                    valor = [idconsulta, fechahora,'extrayendo los hoteles de la competencia para ingresar en la SCR_ANUNCIANTES','352-355', url, '', 1 ]
                    cursor.execute(sqllog, valor)
                    cursor.commit()

                    m += 1
                    #print m
                    Hotel = entrada.find('span', class_="sr-hotel__name").getText()
                    try:    
                        puntuacion = entrada.find('span', re.compile("average")).getText()
                    except:
                        puntuacion = entrada.find('span', re.compile("average"))
                        if puntuacion is None:
                            try:
                                puntuacion = entrada.find('span', re.compile("review-score-badge")).getText()
                            except:
                                puntuacion = entrada.find('span', re.compile("review-score-badge"))
                            if puntuacion is None:
                                puntuacion = 0
                                fechahora = fechaahora()
                                sqllog = ("INSERT INTO SCR_LOG (ID_CONSULTA, FECHA, MENSAJE, LINEA_COD, URL, DETALLE, TIPO) VALUES (?, ?, ?, ?, ?, ?, ?)")
                                valor = [idconsulta, fechahora,'Hotel nuevo no posee puntuacion','267-276', url, '', 3 ]
                                cursor.execute(sqllog, valor)
                                cursor.commit()

                    precio = entrada.find_next_sibling("b", re.compile("sr_gs_price")) 
                    #print precio      
                    if precio is None :
                        #print "entre precio1"
                        preci2 = entrada.find("div", re.compile("sr_gs_rack_rate"))
                        #print preci2
                        if preci2 is None:
                            #print "entre precio2"
                            precio = entrada.find("div", re.compile("totalPrice"))
                            tipo = 1
                        else:
                            #print "entre precio3"
                            precio = preci2.find("b", re.compile("sr_gs_price"))
                            tipo = 2
                        #print preci2
                                    
                        if precio is None:
                            Price = 0
                            fechahora = fechaahora()
                            sqllog = ("INSERT INTO SCR_LOG (ID_CONSULTA, FECHA, MENSAJE, LINEA_COD, URL, DETALLE, TIPO) VALUES (?, ?, ?, ?, ?, ?, ?)")
                            valor = [idconsulta, fechahora,'Precio no encontrado por hotel Agotado','278-283', url, '', 3 ]
                            cursor.execute(sqllog, valor)
                            cursor.commit()
                        else:
                            prec = precio.next_element
                            #print prec
                            if prec == '':
                                Price = 0
                            else:    
                                #print prec                        
                                pre =u' '.join((prec)).encode('utf-8').strip()
                                variable = True
                                #pre =str(prec)
                                #print pre
                                l = 0
                                Price = ""
                                limit = len(pre)-5
                                #print limit
                                if limit>53:
                                    limit = len(pre)-9
                                while l < len(pre):
                                    if pre[l].isdigit():
                                        if l >= limit and tipo ==1:
                                            Price = Price + pre[l]
                                            #limit += 2
                                        elif tipo == 2:
                                            Price = Price + pre[l]
                                        l += 1
                                    else:
                                        if pre[l]=='.':
                                            Price = Price
                                        l += 1
                                #print Price 
                    else:
                        prec = precio
                        #print prec
                        variable = True
                        pre =str(prec)
                        l = 0
                        Price = ""
                        limit = len(pre)-5
                        while l < len(pre):
                            if pre[l].isdigit():
                                Price = Price + pre[l]
                                l += 1
                            else:
                                if pre[l]=='.':
                                    Price = Price
                                l += 1
                    #print Price
                    a = 0   
                    if puntuacion != 0:
                        #print puntuacion
                        puntuacion = u' '.join((puntuacion)).encode('utf-8').strip()
                        #print puntuacion
                        if puntuacion[a].isdigit or b!=5:
                            puntuacion = puntuacion[a]
                            #print puntuacion
                            b=5
                        a += 1
                        if puntuacion == 0 or puntuacion=='' or puntuacion==" ":
                            puntuacion = 0
                            #print puntuacion
                        try:
                            #print "try %s" %puntuacion
                            puntuacion = int(puntuacion)
                        except:
                            #raise
                            #print puntuacion
                            puntuacion = 0

                    if Price == '':
                        Price = 0
                        fechahora = fechaahora()
                        sqllog = ("INSERT INTO SCR_LOG (ID_CONSULTA, FECHA, MENSAJE, LINEA_COD, URL, DETALLE, TIPO) VALUES (?, ?, ?, ?, ?, ?, ?)")
                        valor = [idconsulta, fechahora,'Precio no Encontrado, revisar la clase','278-336', url, '', 2 ]
                        cursor.execute(sqllog, valor)
                        cursor.commit()
                            
                    if Price==0:
                        print 'Hotel Ocupado'
                        cadena = "posicion: %d Hotel: %s Precio:%s Puntuacion:%s " %(m, Hotel, Price, puntuacion)
                        fechahora = fechaahora()
                        sqllog = ("INSERT INTO SCR_LOG (ID_CONSULTA, FECHA, MENSAJE, LINEA_COD, URL, DETALLE, TIPO) VALUES (?, ?, ?, ?, ?, ?, ?)")
                        valor = [idconsulta, fechahora,'Hotel ocupado no se toma en cuenta','278-336', url, cadena, 2 ]
                        cursor.execute(sqllog, valor)
                        cursor.commit()
                        m -= 1
                    else:
                        Price = int(Price)
                        Fecha = str(fecha)
                        Fechasal = str(Fechasal)
                        #se recorre la lista de hoteles 
                        a = 0
                        for s in listhotl:
                            #print s
                            shotl =s.replace(' ','')
                            shotl = u' '.join((shotl)).encode('utf-8').strip()
                            hotels = Hotel.replace(' ','')
                            hotels = u' '.join((hotels)).encode('utf-8').strip()
                            #print shotl
                            #print hotels
                            if hotels == shotl:
                                idhotel = listhotlid[a]
                                print 'Comparando Hoteles'
                                #Ingresar dato en anunciantes hoteles
                                in_precio = Price / c[10]
                                sqlhotl = ("INSERT INTO SCR_ANUNCIANTES(ID_ANUNCIO, FECHAI, FECHAF, ORDEN, ID_PORTAL, PRECIO, ID_CONSULTA, RATIO) VALUES (?, ?, ?, ?, ?, ?, ?, ?)")
                                valorht = [idhotel, Fecha, Fechasal, m, 2, in_precio, idconsulta, puntuacion]
                                cursor.execute(sqlhotl,valorht)
                                cursor.commit()

                                cadena = "posicion: %d Hotel: %s Precio:%s Puntuacion:%s " %(m, Hotel, in_precio, puntuacion)
                                fechahora = fechaahora()
                                sqllog = ("INSERT INTO SCR_LOG (ID_CONSULTA, FECHA, MENSAJE, LINEA_COD, URL, DETALLE, TIPO) VALUES (?, ?, ?, ?, ?, ?, ?)")
                                valor = [idconsulta, fechahora,'Ingresando Anuncio de los hoteles a buscar','313-316', url, cadena, 1 ]
                                cursor.execute(sqllog, valor)
                                cursor.commit()
                            
                                print "posicion: %d \n Hotel: %s \n Precio:%s \n Puntuacion:%s \n *******" %(m, Hotel, in_precio, puntuacion)
                                #m += 1
                                break
                            a += 1
                    

                        a = 0
                        b = 1
                        lenlist=len(listhotlcom)            
                        if lenlist==0 or listhotlcom is None:
                            print 'ingresando hotel de la competenicia'
                            sqlhotl = ("INSERT INTO SCR_COMPETENCIA (TITULO, ID_PORTAL) VALUES (?, ?)")
                            valor = [Hotel, 2]      
                            cursor.execute(sqlhotl,valor)
                            cursor.commit()
                            in_precio = Price / c[10]
                            #print sqlhotl
                            #print valor
                    
                            fechahora = fechaahora()
                            sqllog = ("INSERT INTO SCR_LOG (ID_CONSULTA, FECHA, MENSAJE, LINEA_COD, URL, DETALLE, TIPO) VALUES (?, ?, ?, ?, ?, ?, ?)")
                            valor = [idconsulta, fechahora,'Ingresando nuevo hotel de la competencia','352-355', url, '', 2 ]
                            cursor.execute(sqllog, valor)
                            cursor.commit()
                
                            sqltop = ("SELECT TOP 1 ID_COMPETENCIA FROM SCR_COMPETENCIA WHERE ID_PORTAL=2 ORDER BY ID_COMPETENCIA DESC")
                            cursor.execute(sqltop)
                            resulth = cursor.fetchone()
                            idhotel = resulth[0]
                            #print idhotel

                            fechahora = fechaahora()
                            sqllog = ("INSERT INTO SCR_LOG (ID_CONSULTA, FECHA, MENSAJE, LINEA_COD, URL, DETALLE, TIPO) VALUES (?, ?, ?, ?, ?, ?, ?)")
                            valor = [idconsulta, fechahora,'Seleccionando el ultimo hotel ingresado de Booking','365-368', url, '', 2 ]
                            cursor.execute(sqllog, valor)
                            cursor.commit()

                            sqlhotlcom = ("INSERT INTO SCR_ANUNCIANTES (ID_COMPETENCIA, FECHAI, FECHAF, ORDEN, ID_PORTAL, PRECIO, ID_CONSULTA, RATIO) VALUES (?, ?, ?, ?, ?, ?, ?, ?)")
                            valorcom = [idhotel, Fecha, Fechasal, m, 2, in_precio, idconsulta, puntuacion]  
                            cursor.execute(sqlhotlcom,valorcom)
                            cursor.commit()
                            
                            cadena = "posicion: %d Hotel: %s Precio:%s Puntuacion:%s " %(m, hoteltex, in_precio, puntuacion) 
                            fechahora = fechaahora()
                            sqllog = ("INSERT INTO SCR_LOG (ID_CONSULTA, FECHA, MENSAJE, LINEA_COD, URL, DETALLE, TIPO) VALUES (?, ?, ?, ?, ?, ?, ?)")
                            valor = [idconsulta, fechahora,'Ingresando anuncio de hotel de la competencia','377-380', url, cadena, 2 ]
                            cursor.execute(sqllog, valor)
                            cursor.commit()
                            #print "posicion: %d \n Hotel: %s \n Precio:%s \n Puntuacion:%s \n *******" %(m, hoteltex, in_precio, puntuacion)
                            break
                        else:
                            for s in listhotlcom:
                                shotl =s.replace(' ','')
                                shotl = u' '.join((shotl)).encode('utf-8').strip()
                                #print shotl
                                hotels = Hotel.replace(' ','')
                                hotels = u' '.join((hotels)).encode('utf-8').strip()
                                #print hotels
                                hoteltex = u' '.join((Hotel)).encode('utf-8')
                                if hotels == shotl:
                                    idhotel = listhotlcomid[a]
                                    in_precio = Price / c[10]
                                    print 'comparando hoteles de la competencia'
                                    #Ingresar a una lista los hoteles
                                    sqlhotlcom = ("INSERT INTO SCR_ANUNCIANTES (ID_COMPETENCIA, FECHAI, FECHAF, ORDEN, ID_PORTAL, PRECIO, ID_CONSULTA, RATIO) VALUES (?, ?, ?, ?, ?, ?, ?, ?)")
                                    valorcom = [idhotel, Fecha, Fechasal, m, 2, in_precio, idconsulta, puntuacion]
                                    cursor.execute(sqlhotlcom,valorcom)
                                    cursor.commit()
                                    #print sqlhotlcom
                                    #print valorcom
                                    cadena = "posicion: %d Hotel: %s Precio:%s Puntuacion:%s " %(m, hoteltex, in_precio, puntuacion) 
                                   
                                    fechahora = fechaahora()
                                    sqllog = ("INSERT INTO SCR_LOG (ID_CONSULTA, FECHA, MENSAJE, LINEA_COD, URL, DETALLE, TIPO) VALUES (?, ?, ?, ?, ?, ?, ?)")
                                    valor = [idconsulta, fechahora,'Ingresando Anuncio de los hoteles de la competencia','339-342', url, cadena, 2 ]
                                    cursor.execute(sqllog, valor)
                                    cursor.commit()
                                         
                                    #print "posicion: %d \n Hotel: %s \n Precio:%s \n Puntuacion:%s \n *******" %(m, hoteltex, in_precio, puntuacion)

                                    break
                                elif b == lenlist:
                                    print 'ingresando hotel de la competenicia'
                                    sqlhotl = ("INSERT INTO SCR_COMPETENCIA (TITULO, ID_PORTAL) VALUES (?, ?)")
                                    valor = [Hotel, 2]      
                                    cursor.execute(sqlhotl,valor)
                                    cursor.commit()
                                    #print sqlhotl
                                    #print valor
                        
                                    fechahora = fechaahora()
                                    sqllog = ("INSERT INTO SCR_LOG (ID_CONSULTA, FECHA, MENSAJE, LINEA_COD, URL, DETALLE, TIPO) VALUES (?, ?, ?, ?, ?, ?, ?)")
                                    valor = [idconsulta, fechahora,'Ingresando nuevo hotel de la competencia','352-355', url, '', 2 ]
                                    cursor.execute(sqllog, valor)
                                    cursor.commit()
                
                                    sqltop = ("SELECT TOP 1 ID_COMPETENCIA FROM SCR_COMPETENCIA WHERE ID_POTRAL=2 ORDER BY ID_COMPETENCIA DESC")
                                    cursor.execute(sqltop)
                                    resulth = cursor.fetchone()
                                    idhotel = resulth[0]
                                    #print idhotel

                                    fechahora = fechaahora()
                                    sqllog = ("INSERT INTO SCR_LOG (ID_CONSULTA, FECHA, MENSAJE, LINEA_COD, URL, DETALLE, TIPO) VALUES (?, ?, ?, ?, ?, ?, ?)")
                                    valor = [idconsulta, fechahora,'Seleccionando el ultimo hotel ingresado de Booking','365-368', url, '', 2 ]
                                    cursor.execute(sqllog, valor)
                                    cursor.commit()

                                    sqlhotlcom = ("INSERT INTO SCR_ANUNCIANTES (ID_COMPETENCIA, FECHAI, FECHAF, ORDEN, ID_PORTAL, PRECIO, ID_CONSULTA, RATIO) VALUES (?, ?, ?, ?, ?, ?, ?, ?)")
                                    valorcom = [idhotel, Fecha, Fechasal, m, 2, in_precio, idconsulta, puntuacion]  
                                    cursor.execute(sqlhotlcom,valorcom)
                                    cursor.commit()

                                    cadena = "posicion: %d Hotel: %s Precio:%s Puntuacion:%s " %(m, hoteltex, in_precio, puntuacion) 
                                    fechahora = fechaahora()
                                    sqllog = ("INSERT INTO SCR_LOG (ID_CONSULTA, FECHA, MENSAJE, LINEA_COD, URL, DETALLE, TIPO) VALUES (?, ?, ?, ?, ?, ?, ?)")
                                    valor = [idconsulta, fechahora,'Ingresando anuncio de hotel de la competencia','377-380', url, cadena, 2 ]
                                    cursor.execute(sqllog, valor)
                                    cursor.commit()
                                    #print "posicion: %d \n Hotel: %s \n Precio:%s \n Puntuacion:%s \n *******" %(m, hoteltex, in_precio, puntuacion)
                                    break
                                a += 1
                                b += 1
                                # Se imprime el resultado de la busqueda
                    
               
  
                i += 1
        
            fechahora = fechaahora()
            sqllog = ("INSERT INTO SCR_LOG (ID_CONSULTA, FECHA, MENSAJE, LINEA_COD, URL, DETALLE, TIPO) VALUES (?, ?, ?, ?, ?, ?, ?)")
            valor = [idconsulta, fechahora,'fin de la busqueda','401', url, '', 2 ]
            cursor.execute(sqllog, valor)
            cursor.commit()

            fechahora = fechaahora()
            sqllog = ("UPDATE SCR_ESTADO SET FECHA=?, ESTADO=? WHERE ID_PORTAL=2")
            valor = [fechahora, 1 ]
            cursor.execute(sqllog, valor)
            cursor.commit()
        
            print "Datos Obtenidos completos"
            #print "enviado"
        except:
            print "No se ha podido cargar la pagina vuelva a intentarlo"
            fechahora = fechaahora()
            sqllog = ("INSERT INTO SCR_LOG (ID_CONSULTA, FECHA, MENSAJE, LINEA_COD, URL, DETALLE, TIPO) VALUES (?, ?, ?, ?, ?, ?, ?)")
            valor = [idconsulta, fechahora,'No se ha podido cargar la pagina al ordenar vuelva a intentarlo','401', url, '', 3 ]
            cursor.execute(sqllog, valor)
            cursor.commit()

            fechahora = fechaahora()
            sqllog = ("UPDATE SCR_ESTADO SET FECHA=?, ESTADO=? WHERE ID_PORTAL=2")
            valor = [fechahora, 0 ]
            cursor.execute(sqllog, valor)
            cursor.commit()
            raise
    else:
        sqllog = ("UPDATE SCR_CONSULTAS SET ESTADO=? WHERE ID_CONSULTA=?")
        valor = [0, idconsulta]
        cursor.execute(sqllog, valor)
        cursor.commit()
        print "La consulta se ejecutara en %s dias" % str(dias.days)
cnn.close()