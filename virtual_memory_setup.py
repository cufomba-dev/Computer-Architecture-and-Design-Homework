# Copyright (c) 2015 Jason Power
# Modified existing two_level.py for virtual memory experiment

# import the m5 (gem5) library created when gem5 is built
import m5

# import all of the SimObjects
from m5.objects import *

# Add the common scripts to our path
m5.util.addToPath("../../")

# import the caches which we made
from caches import *

# import the SimpleOpts module
from common import SimpleOpts

# Default to running 'hello', use the compiled ISA to find the binary
# grab the specific path to the binary
thispath = os.path.dirname(os.path.realpath(__file__))
default_binary = os.path.join(
    thispath,
    "../../../",
    "stress_tlb",
)

# Binary to execute
SimpleOpts.add_option("binary", nargs="?", default=default_binary)
SimpleOpts.add_option("--page-size", type=str, default="4KiB")
SimpleOpts.add_option("--itlb-size", type=int, default=64)
SimpleOpts.add_option("--itlb-assoc", type=int, default=4)
SimpleOpts.add_option("--dtlb-size", type=int, default=64)
SimpleOpts.add_option("--l2tlb-size", type=int, default=1024,
                     help="L2 TLB size (number of entries)")
SimpleOpts.add_option("--l2tlb-assoc", type=int, default=8,
                     help="L2 TLfB associativity")
SimpleOpts.add_option("--enable-page-table-walker", action="store_true", default=False, help="Enable page table walker")

# Finalize the arguments and grab the args so we can pass it on to our objects
args = SimpleOpts.parse_args()

# create the system we are going to simulate
system = System()

# Set the clock frequency of the system (and all of its children)
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = "1GHz"
system.clk_domain.voltage_domain = VoltageDomain()

# Set up the system
system.mem_mode = "timing"  # Use timing accesses
system.mem_ranges = [AddrRange("4GiB")]  # Create an address 

# Create CPU with virtual memory support
system.cpu = X86TimingSimpleCPU()

# Configure MMU and TLB settings
system.cpu.mmu = X86MMU()

# Configure Instruction TLB
system.cpu.mmu.itb = X86TLB()
system.cpu.mmu.itb.size = args.itlb_size
system.cpu.mmu.itb.entry_type = "instruction"

# Configure Data TLB
system.cpu.mmu.dtb = X86TLB()
system.cpu.mmu.dtb.size = args.dtlb_size
system.cpu.mmu.dtb.entry_type = "data"

# Configure L2 TLB if supported
if hasattr(system.cpu.mmu, 'l2tlb'):
    system.cpu.mmu.l2tlb = X86TLB()
    system.cpu.mmu.l2tlb.size = args.l2tlb_size

# Configure Page Table Walker if enabled
if args.enable_page_table_walker:
    system.cpu.mmu.walker = X86PagetableWalker()
    system.cpu.mmu.walker.num_squash_per_cycle = 4


# Create an L1 instruction and data cache
system.cpu.icache = L1ICache(args)
system.cpu.dcache = L1DCache(args)

# Connect the instruction and data caches to the CPU
system.cpu.icache.connectCPU(system.cpu)
system.cpu.dcache.connectCPU(system.cpu)

# Create a memory bus, a coherent crossbar, in this case
system.l2bus = L2XBar()

# Hook the CPU ports up to the l2bus
system.cpu.icache.connectBus(system.l2bus)
system.cpu.dcache.connectBus(system.l2bus)

# Create L2 cache and connect it to bus
system.l2cache = L2Cache(args)
system.l2cache.connectCPUSideBus(system.l2bus)

# Create memory bus
system.membus = SystemXBar()

# Connect L2 cache to memory bus
system.l2cache.connectMemSideBus(system.membus)

# Create interrupt controller
system.cpu.createInterruptController()
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

# Connect system port
system.system_port = system.membus.cpu_side_ports

# Create DDR3 memory controller
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports


# Configure workload for full system or syscall emulation
system.workload = SEWorkload.init_compatible(args.binary)

# Create process
process = Process()
process.cmd = [args.binary, f"--page-size={args.page_size}"]
system.cpu.workload = process
system.cpu.createThreads()

# Set up root and instantiate
root = Root(full_system=False, system=system)

# Print configuration summary
print("=== Virtual Memory Configuration ===")
print(f"Page Size: {args.page_size}")
print(f"ITLB: {args.itlb_size} entries")
print(f"DTLB: {args.dtlb_size} entries")
print(f"L2 TLB: {args.l2tlb_size} entries, {args.l2tlb_assoc}-way associative")
print(f"Page Table Walker: {'Enabled' if args.enable_page_table_walker else 'Disabled'}")
print("====================================")


# Instantiate and run simulation
m5.instantiate()

print(f"Beginning simulation!")
exit_event = m5.simulate()
print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")

