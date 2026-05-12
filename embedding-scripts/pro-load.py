import h5py
import requests
import json
from gen3.auth import Gen3Auth

pro_file = "survival_rna.h5"

fence_url = "https://mc2dp.data-commons.org/user/data/upload/vector"

m_dict = []
manifest_filename = "proteomics_embeddings.json"

auth = Gen3Auth(refresh_file="mc2dp.creds")
token = auth.get_access_token()

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}


with h5py.File(pro_file) as h5:
	case_ids = list(h5.keys())
	for cid in case_ids:
		file_ids = list(h5[cid].keys())
		for fid in file_ids:
			emb = h5[f"{cid}/{fid}"][:]

			params = {
				"authz":[
					"/open"
				],
				"model": "expr",
				"file_id": fid,
				"embedding": emb.tolist(),
			}

			response = requests.post(url=fence_url, headers=headers, data=json.dumps(params))

			if response.status_code not in [200, 201]:
				print("we had an error")
				print(response.status_code, response.text)
				exit()

			else:
				guid = response.json()["guid"]
				rec = {
					"file_id": fid,
					"guid": guid
				}
				m_dict.append(rec)
			# exit()

		with open(manifest_filename, "w") as file:
			file.write(json.dumps(m_dict))