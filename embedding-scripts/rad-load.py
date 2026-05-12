import h5py
import requests
import json
from gen3.auth import Gen3Auth


# print(auth.get_access_token())

rad_file = "openi-biovilt-frontal-findings-only.h5"




fence_url = "https://m3aicommons.org/user/data/upload/vector"
with h5py.File(rad_file) as h5:
	case_ids = list(h5.keys())

	for case in case_ids:
		print(f"Starting case: {case}")
		auth = Gen3Auth(refresh_file="aicreds.json")
		token = auth.get_access_token()

		headers = {
		    "Authorization": f"Bearer {token}",
		    "Content-Type": "application/json"
		}

		m_dict = []

		patient_ids = list(h5[case].keys())
		for patient in patient_ids:
			study_ids = list(h5[case][patient])
			for study in study_ids:
				file_ids = list(h5[case][patient][study])
				for fid in file_ids:
					embedding = h5[f"{case}/{patient}/{study}/{fid}"][:]

					params = {
						"authz":[
							"/programs/dev/projects/testproject1"
						],
						"model": case,
						"file_id": fid,
						"embedding": embedding.tolist(),
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

		manifest_filename = case + ".json"

		with open(manifest_filename, "w") as file:
			file.write(json.dumps(m_dict))
