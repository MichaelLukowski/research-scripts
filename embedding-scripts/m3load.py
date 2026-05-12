import h5py
import requests
import json
from gen3.auth import Gen3Auth



models = ["hist", "summ", "expr", "text"]


fence_url = "https://m3aicommons.org/user/data/upload/vector"


for m in models:
	filename = m + ".h5"

	manifest_filename = m + ".json"

	auth = Gen3Auth(refresh_file="aicreds.json")
	token = auth.get_access_token()

	headers = {
	    "Authorization": f"Bearer {token}",
	    "Content-Type": "application/json"
	}

	with h5py.File(filename) as h5:
		case_ids = list(h5.keys())
		file_ids = list(h5[case_ids[0]].keys())
		embedding = h5[f"{case_ids[0]}/{file_ids[0]}"][:]
		print(f"Model: {m}")
		m_dict = []
		# m_dict = dd
		for i in range(len(case_ids)):
			cid = case_ids[i]
			fid = list(h5[cid].keys())[0]
			emb = h5[f"{cid}/{fid}"][:]


			params = {
				"authz":[
					"/programs/dev/projects/testproject1"
				],
				"model": m,
				"file_id": fid,
				"embedding": emb.tolist(),
			}


			response = requests.post(url=fence_url, headers=headers, data=json.dumps(params))

			if response.status_code not in [200, 201]:
				print("we had an error")
				print(response.status_code, response.text)

			else:
				guid = response.json()["guid"]
				rec = {
					"file_id": fid,
					"guid": guid
				}
				m_dict.append(rec)


		with open(manifest_filename, "w") as file:
			file.write(json.dumps(m_dict))