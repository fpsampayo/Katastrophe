# coding=utf-8
from app import app
from flask import request, jsonify
import requests
from xml.etree import ElementTree as ET

@app.route('/')
def hello_world():
    return '''
        <h4>Acceso a los servicios web del catastro.</h4>
        <a href="http://katastroph.herokuapp.com/coor?srs=EPSG:4326&x=-8.588562011718752&y=42.28137302193453">
        Ejemplo de petición por coordenadas</a>
    '''


def handler500(message):
    return jsonify({'status': 'false', 'message': message}), 500


def getExtraData(refcat):

    response = requests.get("http://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/OVCCallejero.asmx/Consulta_DNPRC?"
                            "Provincia=&"
                            "Municipio=&"
                            "RC=%s" % refcat)
    if response.status_code == 200:
        ns = {'c': 'http://www.catastro.meh.es/'}
        root = ET.fromstring(response.text.encode('utf-8'))
        tipo = root.find('*//c:cn', ns)

        muni = root.find('*//c:cm', ns).text
        prov = root.find('*//c:cp', ns).text
        masa = None
        parc = None

        if tipo == None:
            masa = refcat[:5]
            parc = refcat[5:7]
        elif tipo.text == 'RU':
            masa = root.find('*//c:cpo', ns).text.zfill(3)
            parc = root.find('*//c:cpa', ns).text.zfill(5)

        return muni, prov, masa, parc


@app.route('/coor')
def coor():
    x = request.args.get('x')
    y = request.args.get('y')
    srs = request.args.get('srs')

    url = "http://ovc.catastro.meh.es//ovcservweb/OVCSWLocalizacionRC/OVCCoordenadas.asmx/Consulta_RCCOOR?&SRS=%s&Coordenada_X=%s&Coordenada_Y=%s" % (str(srs), str(x), str(y))

    response = requests.get(url)

    if response.status_code == 200:
        ns = {'c': 'http://www.catastro.meh.es/'}
        root = ET.fromstring(response.text.encode('utf-8'))
        err = root.find('*//c:err/c:des', ns)
        if err != None:
            print "Error"
            return handler500(err.text)
        pc1 = root.find('*//c:pc1', ns).text
        pc2 = root.find('*//c:pc2', ns).text
        refcat = pc1 + pc2

        muni, prov, masa, parc = getExtraData(refcat)

        urlAccesoSede = "https://www1.sedecatastro.gob.es/CYCBienInmueble/OVCListaBienes.aspx?del=%s&muni=%s&rc1=%s&rc2=%s" % (prov, muni, pc1, pc2)

        r = {'refcat': refcat,
             'provincia': prov,
             'municipio': muni,
             'masa': masa,
             'parcela': parc,
             'accesoSede': urlAccesoSede}

        return jsonify(r)
    else:
        return handler500("Ocurrio un problema conectando con Catastro.")