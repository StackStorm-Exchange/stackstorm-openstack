# Change Log

## 0.7.0
- Add missing zaqarclient
- Add Aodh cli action files and aodhclient to requirements
- Add Neutron cli action files and python-neutronclient to requirements,
  and choose to use neutron cli because some neutron apis hasn't been implemented
  in openstackclient plugin

## 0.6.0

- Added additional project clients to requirements.txt
- Fixed `autogen.py` issue with actions with numeric options
- Tidied up README

## 0.5.0

- Updated action `runner_type` from `run-python` to `python-script`

## 0.4.0

- Rename `config.yaml` to `config.schema.yaml` and update to use schema.
