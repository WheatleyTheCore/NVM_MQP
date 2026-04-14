from lib.excitation_gen import *

for i in [3, 5, 10]:
    generate_log_sweep(i, filename={f'{i}s_sweep'})
    generate_pink_RPMS(i, filename={f'{i}s_pink_RPMS'})