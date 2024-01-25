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