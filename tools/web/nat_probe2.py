import json, requests, urllib3, concurrent.futures as cf
urllib3.disable_warnings()
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36'}
H = ('statelaw.go.ke www.statelaw.go.ke odpc.go.ke www.odpc.go.ke pharmacyboardkenya.org kenha.co.ke kura.go.ke kerra.go.ke nca.go.ke www.ntsa.go.ke kebs.org www.kebs.org kenyaports.go.ke www.kpa.co.ke kcaa.or.ke www.kcaa.or.ke ira.go.ke www.ira.go.ke rba.go.ke www.rba.go.ke www.sasra.go.ke cak.go.ke www.cak.go.ke ca.go.ke www.ca.go.ke epra.go.ke klrc.go.ke www.klrc.go.ke ppra.go.ke www.ppra.go.ke lsk.or.ke nacada.go.ke www.nacada.go.ke kfcb.co.ke www.kfcb.co.ke mct.go.ke kmpdc.go.ke nck.or.ke clinicalofficerscouncil.org kenyanursingcouncil.or.ke tsc.go.ke www.tsc.go.ke cue.ac.ke www.cue.ac.ke tvetauthority.go.ke hakijamii.com fkf.or.ke sportskenya.go.ke nemis.education.go.ke mining.go.ke www.mining.go.ke petroleum.go.ke www.petroleum.go.ke energy.go.ke www.energy.go.ke transport.go.ke www.transport.go.ke lands.go.ke www.lands.go.ke kilimo.go.ke health.go.ke www.health.go.ke labour.go.ke www.labour.go.ke socialprotection.go.ke tourism.go.ke www.tourism.go.ke environment.go.ke www.environment.go.ke water.go.ke www.water.go.ke ict.go.ke www.ict.go.ke trade.go.ke www.trade.go.ke industrialization.go.ke www.industrialization.go.ke cooperatives.go.ke www.cooperatives.go.ke education.go.ke www.education.go.ke defence.go.ke www.mod.go.ke interior.go.ke www.interior.go.ke immigration.go.ke publicservice.go.ke devolution.go.ke www.devolution.go.ke eac.go.ke www.eac.go.ke housing.go.ke gender.go.ke www.gender.go.ke youth.go.ke ncpd.go.ke kws.go.ke wildlife.go.ke www.wildlife.go.ke fisheries.go.ke www.kilimo.go.ke kdb.go.ke coffee.go.ke teaboard.or.ke sugar.go.ke nhif.or.ke nssf.or.ke cbk.go.ke kenyamaritime.go.ke kma.go.ke www.kma.go.ke kebs.go.ke ncia.go.ke wasreb.go.ke nema.go.ke ercke.go.ke rea.go.ke nuclear.go.ke nupea.go.ke www.nupea.go.ke lapsset.go.ke nlc.go.ke ardhi.go.ke cra.go.ke src.go.ke iebc.or.ke www.iebc.or.ke orpp.or.ke www.orpp.or.ke eacc.go.ke www.eacc.go.ke odpp.go.ke www.odpp.go.ke ipoa.go.ke www.ipoa.go.ke knchr.org www.knchr.org ombudsman.go.ke www.ombudsman.go.ke ncic.go.ke www.cohesion.go.ke frc.go.ke www.frc.go.ke arbitration.go.ke ncarb.go.ke www.ciarb.or.ke kippra.or.ke').split()


def probe(h):
    try:
        r = requests.get(f'https://{h}/wp-json/wp/v2/media', params={'mime_type': 'application/pdf', 'per_page': 1},
                         headers=UA, timeout=(10, 25), verify=False)
        return h, r.status_code, r.headers.get('X-WP-Total')
    except Exception as e:  # noqa: BLE001
        return h, type(e).__name__, None


res = {}
with cf.ThreadPoolExecutor(12) as ex:
    for h, s, t in ex.map(probe, sorted(set(H))):
        res[h] = (s, t)
        if t:
            print(h, s, t, flush=True)
json.dump(res, open(r'kenya-law-work\nat_probe2.json', 'w'), indent=1)
