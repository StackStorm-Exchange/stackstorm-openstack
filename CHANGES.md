# Change Log

## 0.8.1

- Correct problem with error reporting on Python 3

## 0.8.0

- Add group actions

## 0.7.3

- Python 3 fixups
- Add explicit support for Python 2 and 3

## 0.7.2

- Update OpenStack authenticate environment variables for Keystone v3
  compatible.

## 0.7.1

- Version bump to fix tagging issue. No code changes.

## 0.7.0

- Rename neutron actions to neutron.<name> to avoid conflict in user end
- Rename aodh actions to aodh.<name>
- Add missing zaqarclient
- Add Aodh action files and aodhclient to requirements
- Add Neutron action files and python-neutronclient to requirements.
  Integrate neutronclient because some neutron APIs hasn't been implemented
  in openstackclient plugin
- Fix some configuration files' format

## 0.6.0

- Added additional project clients to requirements.txt
- Fixed `autogen.py` issue with actions with numeric options
- Tidied up README

## 0.5.0

- Updated action `runner_type` from `run-python` to `python-script`

## 0.4.0

- Rename `config.yaml` to `config.schema.yaml` and update to use schema.
