#global ATF_VAL_EXTENSION_FILE
#global VAL_EXTENSION_IGNORE
#global begin_pattern
#global end_pattern
#global end_of_file_pattern
#global LINE_SIZE_MIN
#global SPECIAL_LINES

LINE_SIZE_MIN = 10
begin_pattern   = '##### VALIDATION EXTENSION PATTERN: Begin #####'
end_pattern     = '##### VALIDATION EXTENSION PATTERN: End #######\n'
end_of_file_pattern = '##### VALIDATION EXTENSION PATTERN: End of file#######'

SPECIAL_LINES = [
'#endif /* _POSIX_SOURCE */',
'                PREAMBLE_LENGTH2_WR (7);',
'	tmp = *offset - XGENE_NS_BL33_IMAGE_OFFSET;',
#'        Name(_CCA, ONE)',
'		return -EPERM;',
'		return 0;',
'  VirtualMemoryTable[Index].Attributes   = ARM_MEMORY_REGION_ATTRIBUTE_DEVICE;'
]

SDL_PCDS_SECTION_HEADER=[
'#################################################################',
'#                             PCDs                              #',
'#################################################################',
'#',
'# PcdsFixedAtBuild',
'#'
]


ATF_VAL_EXTENSION_IGNORE = [
'build',
'Build',
'.git',
'.gitignore',
'aptio/build.sh',
]

ATF_VAL_EXTENSION_FILE = [
#'atf/Makefile',
#'atf/bl1/bl1_main.c',
#'atf/include/stdlib/sys/errno.h',
#'atf/plat/apm/xgene/platform.mk',
#'atf/plat/apm/xgene/common/xgene_bl1_setup.c',
#'atf/plat/apm/xgene/common/xgene_delay_timer.c',
#'atf/plat/apm/xgene/common/drivers/i2c/i2c.c',
#'atf/plat/apm/xgene/common/drivers/smpro/smprolib.mk',
#'atf/plat/apm/xgene/common/services/apm_oem_svc/i2c_proxy/i2c_proxy.c',
#'atf/plat/apm/xgene/include/platform_def.h',
#'atf/plat/apm/xgene/include/board/config_clk.h',
#'atf/plat/apm/xgene/include/board/config_i2c.h',
#'atf/plat/apm/xgene/include/board/config_spi.h',
#'atf/plat/apm/xgene/include/board/eagle/config.h',
#'atf/plat/apm/xgene/include/board/osprey/config.h',
#'atf/plat/apm/xgene/include/drivers/i2c.h',
#'atf/plat/apm/xgene/include/skylark/skylark_soc.h',
#'atf/plat/apm/xgene/include/skylark/xgene_def.h',
#'atf/plat/apm/xgene/soc/skylark/drivers/ahbc/ahbc.c'
]





APTIO_VAL_EXTENSION_IGNORE = [
'build',
'Build',
'.git',
'.gitignore',
'build.sh',
]




APTIO_VAL_EXTENSION_FILE = [
#'aptio/AmiModulePkg/Bds/Bds.sdl',
#'aptio/ArmPlatformPkg/APMXGenePkg/Applications/LinuxLoaderApp/LinuxLoaderApp.c',
#'aptio/ArmPlatformPkg/APMXGenePkg/Applications/LinuxLoaderApp/LinuxLoaderAppBin.inf',
#'aptio/ArmPlatformPkg/APMXGenePkg/Applications/Applications.cif',
#'aptio/ArmPlatformPkg/APMXGenePkg/Applications/Applications.sdl',
#'aptio/ArmPlatformPkg/APMXGenePkg/Drivers/XGeneEnet/SnpDxe.c',
#'aptio/ArmPlatformPkg/APMXGenePkg/Drivers/XGeneEnet/XgMgmtMac.c',
#'aptio/ShellBinPkg/FullShell/FullShell.inf',
#'aptio/ShellBinPkg/ShellBinPkg.sdl',
#'aptio/SkylarkPkg/SkylarkPkg.dec',
#'aptio/SkylarkPkg/SkylarkPkg.sdl',
#'aptio/Osprey.sdl',
#'aptio/Osprey.veb'
]


LINUX_VAL_EXTENSION_FILE = [
#'linux/arch/arm64/configs/xgene_defconfig',
#'linux/arch/arm64/Kconfig',
#'linux/drivers/net/ethernet/apm/xgene-v2/mac.c',
#'linux/drivers/acpi/acpi_apd.c',
#'linux/drivers/mtd/devices/m25p80.c',
#'linux/drivers/mtd/ofpart.c',
#'linux/drivers/spi/Kconfig',
#'linux/drivers/spi/Makefile',
#'linux/drivers/spi/spi-xgene.c',
#'linux/drivers/spi/spi-xgene.h',
#'linux/drivers/ata/ahci_xgene.c',
#'linux/drivers/ata/libata-core.c',
#'linux/drivers/ata/libata-eh.c',
#'linux/drivers/Makefile'
]

LINUX_VAL_EXTENSION_IGNORE = [
'.git',
'.gitignore',
'block',
'certs',
'crypto',
'Documentation',
'firmware',
'fs',
'init',
'ipc',
'kernel',
'lib',
'mm',
'net',
'samples',
'scripts',
'security',
'sound',
'tools',
'usr',
'virt',
'COPYING',
'CREDITS',
'Image'
]


