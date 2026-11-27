import json, requests, urllib3, concurrent.futures as cf
urllib3.disable_warnings()
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36'}
H = ('kra.go.ke centralbank.go.ke cma.or.ke nema.go.ke epra.go.ke statelaw.go.ke klrc.go.ke treasury.go.ke health.go.ke '
     'kilimo.go.ke environment.go.ke ict.go.ke labour.go.ke education.go.ke energy.go.ke transport.go.ke lands.go.ke '
     'interior.go.ke judiciary.go.ke ca.go.ke ppra.go.ke rba.go.ke ira.go.ke sasra.go.ke nca.go.ke kebs.org ntsa.go.ke '
     'odpc.go.ke wra.go.ke kws.go.ke kenyaforestservice.org landcommission.go.ke eacc.go.ke iebc.or.ke cak.go.ke '
     'agricultureauthority.go.ke kephis.org pcpb.go.ke kdb.go.ke afa.go.ke nacada.go.ke ppb.go.ke kmpdc.go.ke '
     'nck.or.ke nita.go.ke kipi.go.ke copyright.go.ke brs.go.ke nlc.go.ke crakenya.org cra.go.ke src.go.ke '
     'publicservice.go.ke psc.go.ke tsc.go.ke cue.ac.ke tvetauthority.go.ke knqa.go.ke mining.go.ke petroleum.go.ke '
     'nemakenya.org kenyamaritime.go.ke kma.go.ke kpa.co.ke kcaa.or.ke ncpd.go.ke ncpwd.go.ke cooperatives.go.ke '
     'tradeandindustry.go.ke industrialization.go.ke tourism.go.ke sportsheritage.go.ke water.go.ke wasreb.go.ke '
     'nlc.go.ke ardhi.go.ke housing.go.ke defence.go.ke foreignaffairs.go.ke mfa.go.ke immigration.go.ke '
     'cbk.go.ke frc.go.ke arbitration.go.ke ombudsman.go.ke knchr.org ipoa.go.ke oagdoj.go.ke ag.go.ke '
     'kenyalawreform.go.ke govtprinter.go.ke statehouse.go.ke president.go.ke parliament.go.ke senate.go.ke '
     'kecosce.go.ke kenyaports.go.ke kentrade.go.ke kippra.or.ke kfcb.co.ke mct.go.ke dciconnect.go.ke '
     'kfs.go.ke kalro.org fisheries.go.ke kenyafisheries.go.ke kemfri.org vetboard.co.ke dvs.go.ke '
     'nhif.or.ke sha.go.ke nssf.or.ke hela.go.ke helb.co.ke cofek.co.ke competitionauthority.go.ke '
     'ercke.go.ke rea.go.ke kengen.co.ke kplc.co.ke npo.go.ke nwh.go.ke curriculumdeveloper.go.ke kicd.ac.ke').split()


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
json.dump(res, open(r'kenya-law-work\nat_probe.json', 'w'), indent=1)
