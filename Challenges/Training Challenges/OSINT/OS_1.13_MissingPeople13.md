# OS_1.13 — Missing people 13

---

## Problem description

Thirteenth challenge in the "Missing people" series. It asks to determine the exact sentencing date in 2016 when Anthony was condemned to prison.

Flag format: `MM/DD/YYYY`.

## Recon

Commercial background check services frequently place public judicial and incarceration records behind aggressive paywalls. In the United States, however, state government agencies maintain authoritative, open-access public registries under state freedom of information mandates.

For individuals processed through the Arizona correctional system, the **Arizona Department of Corrections, Rehabilitation & Reentry (ADCRR)** hosts an authoritative public database (`inmatedatasearch.azcorrections.gov`).

Because municipal and state-level `.gov` portals in the US routinely implement geographic firewalling (dropping non-domestic network connections or blocking European IP pools due to compliance and DDOS policies), querying this infrastructure requires an active **VPN connection routing through a United States exit node**.

## Solution, step by step

1. Initialize a **VPN connection to a U.S. server** to circumvent network timeouts on the state domain.
2. Navigate to the **[ADCRR Inmate Datasearch](https://inmatedatasearch.azcorrections.gov/)** portal.
3. Query the inmate registry using the biographical indicators confirmed in previous challenges:
* **Last Name:** `Ginnetti`
* **First Initial:** `A`
* **Gender:** `Male`
* **Current Status:** `Inactive`


4. Select the matching entry for **Anthony M Ginnetti** (Inmate ID **`309437`**).
5. Navigate to the **Commitment and Sentence Information** table.
6. Inspect the rows corresponding to the 2016 judicial dispositions (`Commit# A01` / `B01`):

```text
Commit#:         A01
Court Cause#:    2011127554001
Offense Date:    11/02/2010
Sentence Date:   04/06/2016
Sentence Status: Imposed
Crime:           MARIJUANA VIOLATION

```

7. Extract the **Sentence Date** formatted according to the requested `MM/DD/YYYY` specification: **`04/06/2016`**.

## Flag

```
****************
```

## What I learned

* **Authoritative Open Records vs. Commercial Paywalls:** Official state and county correctional registries provide direct, verified criminal history and sentencing records without requiring commercial aggregator subscriptions.
* **Government Portal Geo-Fencing:** State-level administrative web services (`.gov`) frequently drop international traffic; regional proxying/VPN tunneling is essential for non-domestic OSINT investigations.
* **Judicial Field Discrimination:** Dissecting inmate records requires strictly distinguishing between the date of the criminal act (**Offense Date**), the judicial conviction (**Sentence Date**), and facility intake (**Admission Date**).