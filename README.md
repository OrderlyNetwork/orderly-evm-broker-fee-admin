# Orderly EVM Broker Fee Admin
[![Python version](https://img.shields.io/badge/Python-3.10-bright)](https://www.python.org/downloads/)
[![Documentation](https://img.shields.io/badge/docs-latest-blue)](https://binance-connector.readthedocs.io/en/stable/)
[![Code Style](https://img.shields.io/badge/code_style-black-black)](https://black.readthedocs.io/en/stable/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This is a lightweight library that works as a tool to configure broker default rates and user's rates.

Main functions:
- Configure broker default rates
- Automatically update the latest rates based on user's volumes
- Configure special rates for users

## Installation

```bash
pip install -r requirements.txt
```

## Configurations

- account_id, api_key, api_secret: broker admin acount information
- orderly_endpoint: API URL
- statistical_days: The latest rate period is calculated based on volume, with 30 representing the last 30 days
- fee_tier: The broker's self-defined rate tier
- special_rate_whitelists: When configuring a special rate for a user, the account_id of the user is recorded. Users of this list will not automatically update rates
- startup_batch_update_fee: True: The user rate is automatically updated when the service is started, otherwise it is periodically executed every day

Usage examples:
```yaml
common:
  account_id: '0x...'
  api_key: ed25519:...
  api_secret: ed25519:...j
  orderly_endpoint: https://api-evm.orderly.network
  statistical_days: 30
rate:
  fee_tier:
  - maker_fee: 0.03%
    taker_fee: 0.06%
    tier: '1'
    volume_max: 500000
    volume_min: 0
  - maker_fee: 0.024%
    taker_fee: 0.054%
    tier: '2'
    volume_max: 2500000
    volume_min: 500000
  - maker_fee: 0.018%
    taker_fee: 0.048%
    tier: '3'
    volume_max: 10000000
    volume_min: 2500000
  - maker_fee: 0.012%
    taker_fee: 0.042%
    tier: '4'
    volume_max: 100000000
    volume_min: 10000000
  - maker_fee: 0.006%
    taker_fee: 0.036%
    tier: '5'
    volume_max: 250000000
    volume_min: 100000000
  - maker_fee: 0%
    taker_fee: 0.03%
    tier: '6'
    volume_max: null
    volume_min: 250000000
  special_rate_whitelists:
  - '0x'
  startup_batch_update_fee: true

```

## Usage method
1. Help information
```shell 
    python3 app/main.py

    Help Information(Option,Parameters):
    - update-broker-default-fee <maker fee> <taker fee> 
    - update-user-special-rate <account_id> <maker fee> <taker fee> 
    - update-user-rate-base-volume
    Description: The fee unit uses percentiles, e.g. 0.0003 = 0.03%
    
    Examples: python3 app/main.py update-broker-default-fee 0.0003 0.0005
```
2. Update broker default rates
```shell
    python3 app/main.py update-broker-default-fee 0.001 0.006
```
3. Update special rates for user
```shell
python3 app/main.py update-user-special-rate 0x918ce3f57ce4b2a3920d4a81c772f8a26ce30c9f34792421949d23741338d3b6  0.0001 0.0003
```
4. Start the automatic update user's rates task
```shell 
#Every day at 00:10
python3 app/main.py update-user-rate-base-volume
```
## FAQ
1. What permissions can users use to update broker default rates and their user rates?
Only the Broker Admin account has permission to make changes. It is a special account that the broker needs to contact the business team and the Orderly authorizes this account
2. What can the Broker Admin account do?
    - Query the current rates for all Broker users
    - Update broker's default rate configuration
    - Update users' rate configuration in batches
    - Restore users' rates to default rates in batches

3. What are the functions of Orderly EVM Broker Fee Admin?
    - Execute instructions to modify the Broker’s default rate
    - Periodically adjust users' rates in batches based on the defined 30-day transaction volume rate level configuration
    - Execute instructions to add special user fixed rates

4. What is special user fixed rate configuration?
After configuring the special user fixed rate configuration, when the scheduled task updates the user rate configuration based on the 30-day transaction volume every day, this part of the users will not be adjusted.
For the whitelist list of special users (check the broker.yaml configuration file), please refer to the following example:
```yaml
rate:
  special_rate_whitelists:
  - '0x918ce3f57ce4b2a3920d4a81c772f8a26ce30c9f34792421949d23741378d3b7'
```
5. How to configure the broker's fee rate tier (configuring the broker.yaml file)?
Examples are as follows:
```yaml
rate:
  fee_tier:
  - maker_fee: 0.03%
    taker_fee: 0.06%
    tier: '1'
    volume_max: 500000
    volume_min: 0
  - maker_fee: 0.024%
    taker_fee: 0.054%
    tier: '2'
    volume_max: 2500000
    volume_min: 500000
  - maker_fee: 0.018%
    taker_fee: 0.048%
    tier: '3'
    volume_max: 10000000
    volume_min: 2500000
  - maker_fee: 0.012%
    taker_fee: 0.042%
    tier: '4'
    volume_max: 100000000
    volume_min: 10000000
  - maker_fee: 0.006%
    taker_fee: 0.036%
    tier: '5'
    volume_max: 250000000
    volume_min: 100000000
  - maker_fee: 0%
    taker_fee: 0.03%
    tier: '6'
    volume_max: null
    volume_min: 250000000
```
6. How to view the help information of the Orderly EVM Broker Fee Admin tool?

```python
    python3 app/main.py

    Help Information(Option,Parameters):
    - update-broker-default-fee <maker fee> <taker fee> 
    - update-user-special-rate <account_id> <maker fee> <taker fee> 
    - update-user-rate-base-volume
    Description: The fee unit uses percentiles, e.g. 0.0003 = 0.03%
    
    Examples: python3 app/main.py update-broker-default-fee 0.0003 0.0005
```
7. How to modify the broker’s default rate?

```python 
python3 app/main.py update-broker-default-fee 0.001 0.006
```
8. How to add a special user fixed rate (after it is added successfully, its rate will not be updated regularly based on  volume)?
```python 
python3 app/main.py update-user-special-rate 0x918ce3f57ce4b2a3920d4a81c772f8a26ce30c9f34792421949d23741378d3b7 0.0001 0.0003
添加成功后，会将固定费率配置用户account_id记录到配置文件config/broker.yaml
rate:
  special_rate_whitelists:
  - '0x918ce3f57ce4b2a3920d4a81c772f8a26ce30c9f34792421949d23741378d3b7'
```

9. How to delete the special user fixed fee (after successful deletion, its rate will not be updated regularly based on  volume)?
Update the config/broker.yaml configuration file and delete the corresponding account_id in special_rate_whitelists.
```yaml
rate:
  special_rate_whitelists:
  - '0x918ce3f57ce4b2a3920d4a81c772f8a26ce30c9f34792421949d23741378d3b7'
```
10. How to automatically update the user fee rate of the broker based on the volume?
It is recommended to run this task no less than 00:10 UTC every day (this logic has been executed at UTC 00:10 by default), and the update scope does not include fixed rate users (special_rate_whitelists)
Default startup_batch_update_fee: True, this logic will be executed first when the service starts
```python
python3 app/main.py update-user-rate-base-volume
```
11. Are there any special precautions when operating the Orderly EVM Broker Fee Admin tool?
- When the project is running, data/logs and data/data will be automatically created in the project directory, which are used to record operation logs and user rate-related data respectively.
- Related operations should be performed in the same project code