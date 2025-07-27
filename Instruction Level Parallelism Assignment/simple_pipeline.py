# import the m5 (gem5) library created when gem5 is built
import m5
import os

# import all of the SimObjects
from m5.objects import *

# import the caches which we made
from caches import *

# import the SimpleOpts module
from common import SimpleOpts

# Create the system
system = System()

# Finalize the arguments and grab the args so we can pass it on to our objects
args = SimpleOpts.parse_args()

# Set the clock frequency of the system (and all of its children)
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz'
system.clk_domain.voltage_domain = VoltageDomain()

# Memory setup
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange("512MiB")]

# Create CPU with O3 pipeline for visualization
system.cpu = X86O3CPU()

# Configure pipeline stages for visualization
system.cpu.fetchWidth = 4
system.cpu.decodeWidth = 4
system.cpu.renameWidth = 4
system.cpu.dispatchWidth = 4
system.cpu.issueWidth = 4
system.cpu.wbWidth = 4
system.cpu.commitWidth = 4

# Create memory bus 
system.membus = SystemXBar()

# Connect system port 
system.system_port = system.membus.cpu_side_ports

# Create an L1 instruction and data cache
system.cpu.icache = L1ICache(args)
system.cpu.dcache = L1DCache(args)

# Connect the caches to CPU and bus
system.cpu.icache.connectCPU(system.cpu)
system.cpu.dcache.connectCPU(system.cpu)
system.cpu.icache.connectBus(system.membus)
system.cpu.dcache.connectBus(system.membus)

# Connect interrupt controller
system.cpu.createInterruptController()

# For X86 only - connect interrupts to memory
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

# Create memory controller 
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

thispath = os.path.dirname(os.path.realpath(__file__))
binary = os.path.join(
    thispath,
    "../../../",
    "tests/test-progs/hello/bin/x86/linux/hello",
)

system.workload = SEWorkload.init_compatible(binary)

# Set workload
process = Process()
process.cmd = [binary]
system.cpu.workload = process
system.cpu.createThreads()

# Enable pipeline visualization features
system.cpu.needsTSO = False
system.cpu.tracer = ExeTracer()

# Instantiate system
root = Root(full_system=False, system=system)
m5.instantiate()

# Run simulation
exit_event = m5.simulate()

print(f'Exiting @ tick {m5.curTick()} because {exit_event.getCause()}')