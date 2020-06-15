import pefile
#import magic
import peutils
import time
import os
import hashlib
import math
import subprocess
import array

#signatures = peutils.SignatureDatabase(os.getcwd()+'/Static/aux_files/userdb.txt')


class PortableExecutable(object):
    """PE analysis."""

    def __init__(self, file_path):
        self.file_path = file_path
        self.pe = None

    def peid_signatures(self):
        """Gets PEID signatures.
        @return: matched signatures or None.
        """
        return []
        # PE singatures module not working
        #return signatures.match(self.pe, ep_only=True)
    
    def imports(self):
        """Gets imported symbols.
        @return: imported symbols dict or None.
        """
        imports = []

        for entry in getattr(self.pe, "DIRECTORY_ENTRY_IMPORT", []):
            dll = entry.dll.decode("utf-8")
            for imported_symbol in entry.imports:
                try:
                    func = imported_symbol.name.decode("utf-8")
                except AttributeError:
                    func = "None"
                imports.append(dll+"_"+func)

            """
            for imported_symbol in entry.imports:
                symbols.append({
                    "address": hex(imported_symbol.address),
                    "name": imported_symbol.name,
                })

            imports.append({
                "dll": entry.dll, #convert_to_printable(entry.dll),
                "imports": symbols,
            })
            """
        return imports

    def exports(self):
        """Gets exported symbols.
        @return: exported symbols dict or None.
        """
        exports = []

        if hasattr(self.pe, "DIRECTORY_ENTRY_EXPORT"):
            for exported_symbol in self.pe.DIRECTORY_ENTRY_EXPORT.symbols:
                exports.append({
                    "address": hex(self.pe.OPTIONAL_HEADER.ImageBase +
                                   exported_symbol.address),
                    "name": exported_symbol.name,
                    "ordinal": exported_symbol.ordinal,
                })

        return exports

    def sections(self):
        """Gets sections.
        @return: sections dict or None.
        """
        sections = []

        for entry in self.pe.sections:
            section = {}
            section["name"] = entry.Name.strip(b"\x00") #convert_to_printable(entry.Name.strip("\x00"))
            section["virtual_address"] = "0x{0:08x}".format(entry.VirtualAddress)
            section["virtual_size"] = "0x{0:08x}".format(entry.Misc_VirtualSize)
            section["size_of_data"] = "0x{0:08x}".format(entry.SizeOfRawData)
            section["entropy"] = entry.get_entropy()
            sections.append(section)

        return sections

    def versioninfo(self):
        """Get version info.
        @return: info dict or None.
        """
        infos = []
        if hasattr(self.pe, "VS_VERSIONINFO"):
            if hasattr(self.pe, "FileInfo"):
                for entry in self.pe.FileInfo:
                    try:
                        if hasattr(entry, "StringTable"):
                            for st_entry in entry.StringTable:
                                for str_entry in st_entry.entries.items():
                                    entry = {}
                                    entry["name"] = str_entry[0] #convert_to_printable(str_entry[0])
                                    entry["value"] = str_entry[1] #convert_to_printable(str_entry[1])
                                    infos.append(entry)
                        elif hasattr(entry, "Var"):
                            for var_entry in entry.Var:
                                if hasattr(var_entry, "entry"):
                                    entry = {}
                                    entry["name"] = var_entry.entry.keys()[0] #convert_to_printable(var_entry.entry.keys()[0])
                                    entry["value"] = var_entry.entry.values()[0] #convert_to_printable(var_entry.entry.values()[0])
                                    infos.append(entry)
                    except:
                        continue

        return infos

    def md5sum(self, blocksize=10240): #10kb
        hash = hashlib.md5()
        with open(self.file_path, "rb") as f:
            for block in iter(lambda: f.read(blocksize), b""):
                hash.update(block)
        return hash.hexdigest()

    def timestamp(self):
        """Get compilation timestamp.
        @return: timestamp or None.
        """
        try:
            pe_timestamp = self.pe.FILE_HEADER.TimeDateStamp
        except AttributeError:
            return None
        return pe_timestamp

    def signature(self):
        # TODO: Change the way it formatting

        p = subprocess.Popen('F:/Ungrd-Research/analyzer/Static/aux_files/DigSignCheck.exe "'+self.file_path+'"', stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        (stdout, stderr) = p.communicate()
        if stdout:
            #sign = {}
            res = stdout.decode("utf-8").replace('\r', '').split("\n")
            if "Chain Not Valid" in res[0]:
                #sign["Trusted"] = False
                return False
            elif "No digital signature found" in res[0]:
                #sign["Trusted"] = None
                return None
            else:
                #sign["Publisher"] = res[1][11:]
                #sign["From"] = res[2][12:]
                #sign["To"] = res[3][10:]
                #sign["Issuer"] = res[4][11:]
                #sign["Thumbprint"] = res[5][13:]
                #sign["Trusted"] = eval(res[6][19:])
                #print(res, self.file_path)
                return eval(res[6][19:])
        else:
            print(stderr)
            return None

    def antidbg(self):
        """
        Number of using anti-debug trick functions
        :return: Int
        """
        antidbg_fn = ('CheckRemoteDebuggerPresent', 'FindWindow', 'GetWindowThreadProcessId', 'IsDebuggerPresent',
                    'OutputDebugString', 'Process32First', 'Process32Next', 'TerminateProcess',
                    'UnhandledExceptionFilter', 'ZwQueryInformation')

        num_fn = 0

        for entry in getattr(self.pe, "DIRECTORY_ENTRY_IMPORT", []):
            symbols = []
            for imported_symbol in entry.imports:
                if imported_symbol.name == None:
                    continue
                for fn in antidbg_fn:
                    if fn in imported_symbol.name.decode("utf-8"):
                        num_fn+=1
        return num_fn

    def entropy(self, data):
        if len(data) == 0:
            return 0.0
        occurences = array.array('L', [0] * 256)
        for x in data:
            occurences[x if isinstance(x, int) else ord(x)] += 1

        entropy = 0
        for x in occurences:
            if x:
                p_x = float(x) / len(data)
                entropy -= p_x * math.log(p_x, 2)

        return entropy

    def resources(self):
        """Extract resources :
        [entropy, size]"""
        resources = []
        if hasattr(self.pe, 'DIRECTORY_ENTRY_RESOURCE'):
            try:
                for resource_type in self.pe.DIRECTORY_ENTRY_RESOURCE.entries:
                    if hasattr(resource_type, 'directory'):
                        for resource_id in resource_type.directory.entries:
                            if hasattr(resource_id, 'directory'):
                                for resource_lang in resource_id.directory.entries:
                                    data = self.pe.get_data(resource_lang.data.struct.OffsetToData,
                                                       resource_lang.data.struct.Size)
                                    size = resource_lang.data.struct.Size
                                    entropy = self.get_entropy(data)

                                    resources.append([entropy, size])
            except Exception as e:
                return resources
        return resources

    """
    def get_version_info(self):
        #Return version infos
        res = {}
        for fileinfo in self.pe.FileInfo:
            if fileinfo.Key == 'StringFileInfo':
                for st in fileinfo.StringTable:
                    for entry in st.entries.items():
                        res[entry[0]] = entry[1]
            if fileinfo.Key == 'VarFileInfo':
                for var in fileinfo.Var:
                    res[var.entry.items()[0][0]] = var.entry.items()[0][1]
        if hasattr(self.pe, 'VS_FIXEDFILEINFO'):
            res['flags'] = self.pe.VS_FIXEDFILEINFO.FileFlags
            res['os'] = self.pe.VS_FIXEDFILEINFO.FileOS
            res['type'] = self.pe.VS_FIXEDFILEINFO.FileType
            res['file_version'] = self.pe.VS_FIXEDFILEINFO.FileVersionLS
            res['product_version'] = self.pe.VS_FIXEDFILEINFO.ProductVersionLS
            res['signature'] = self.pe.VS_FIXEDFILEINFO.Signature
            res['struct_version'] = self.pe.VS_FIXEDFILEINFO.StrucVersion
        return res
    """

    def run(self):

        if not os.path.exists(self.file_path):
            print('path not exists')
            return None

        try:
            self.pe = pefile.PE(self.file_path)
        except pefile.PEFormatError:
            print('pefile.PEFormatError')
            return None

        results = {}
        #results["hash"] = self.md5sum()
        results["size"] = os.path.getsize(self.file_path)
        results["peid_signatures"] = self.peid_signatures()
        results["timestamp"] = self.timestamp()

        results["signature_trusted"] = self.signature()
        results["imports"] = self.imports()
        #results["exports"] = self.exports()
        #results["sections"] = self.sections() #?
        #results["resources"] = self.resources()
        results["anti_dbg"] = self.antidbg()

        if self.pe.is_exe():
            results["filetype"] = "exe"
        elif self.pe.is_dll():
            results["filetype"] = "dll"
        elif self.pe.is_driver():
            results["filetype"] = "sys"
        else:
            results["filetype"] = 'None'

        # Header
        results['Machine'] = self.pe.FILE_HEADER.Machine
        results['Characteristics'] = self.pe.FILE_HEADER.Characteristics

        # Optional header
        results['SizeOfOptionalHeader'] = self.pe.FILE_HEADER.SizeOfOptionalHeader
        results['Magic'] = self.pe.OPTIONAL_HEADER.Magic
        results['MajorLinkerVersion'] = self.pe.OPTIONAL_HEADER.MajorLinkerVersion
        results['MinorLinkerVersion'] = self.pe.OPTIONAL_HEADER.MinorLinkerVersion
        results['SizeOfCode'] = self.pe.OPTIONAL_HEADER.SizeOfCode
        results['SizeOfInitializedData'] = self.pe.OPTIONAL_HEADER.SizeOfInitializedData
        results['SizeOfUninitializedData'] = self.pe.OPTIONAL_HEADER.SizeOfUninitializedData
        results['AddressOfEntryPoint'] = self.pe.OPTIONAL_HEADER.AddressOfEntryPoint
        results['BaseOfCode'] = self.pe.OPTIONAL_HEADER.BaseOfCode
        try:
            results['BaseOfData'] = self.pe.OPTIONAL_HEADER.BaseOfData
        except AttributeError:
            results['BaseOfData'] = 0
        results['ImageBase'] = self.pe.OPTIONAL_HEADER.ImageBase
        results['SectionAlignment'] = self.pe.OPTIONAL_HEADER.SectionAlignment
        results['FileAlignment'] = self.pe.OPTIONAL_HEADER.FileAlignment
        results['MajorOperatingSystemVersion'] = self.pe.OPTIONAL_HEADER.MajorOperatingSystemVersion
        results['MinorOperatingSystemVersion'] = self.pe.OPTIONAL_HEADER.MinorOperatingSystemVersion
        results['MajorImageVersion'] = self.pe.OPTIONAL_HEADER.MajorImageVersion
        results['MinorImageVersion'] = self.pe.OPTIONAL_HEADER.MinorImageVersion
        results['MajorSubsystemVersion'] = self.pe.OPTIONAL_HEADER.MajorSubsystemVersion
        results['MinorSubsystemVersion'] = self.pe.OPTIONAL_HEADER.MinorSubsystemVersion
        results['SizeOfImage'] = self.pe.OPTIONAL_HEADER.SizeOfImage
        results['SizeOfHeaders'] = self.pe.OPTIONAL_HEADER.SizeOfHeaders
        results['CheckSum'] = self.pe.OPTIONAL_HEADER.CheckSum
        results['Subsystem'] = self.pe.OPTIONAL_HEADER.Subsystem
        results['DllCharacteristics'] = self.pe.OPTIONAL_HEADER.DllCharacteristics
        results['SizeOfStackReserve'] = self.pe.OPTIONAL_HEADER.SizeOfStackReserve
        results['SizeOfStackCommit'] = self.pe.OPTIONAL_HEADER.SizeOfStackCommit
        results['SizeOfHeapReserve'] = self.pe.OPTIONAL_HEADER.SizeOfHeapReserve
        results['SizeOfHeapCommit'] = self.pe.OPTIONAL_HEADER.SizeOfHeapCommit
        results['LoaderFlags'] = self.pe.OPTIONAL_HEADER.LoaderFlags
        results['NumberOfRvaAndSizes'] = self.pe.OPTIONAL_HEADER.NumberOfRvaAndSizes

        # Sections
        results['SectionsNb'] = len(self.pe.sections)

        if results['SectionsNb'] == 0:
            results['SectionsMeanEntropy'] = 0
            results['SectionsMinEntropy'] = 0
            results['SectionsMaxEntropy'] = 0
            results['SectionsMeanRawsize'] = 0
            results['SectionsMinRawsize'] = 0
            results['SectionsMaxRawsize'] = 0
            results['SectionsMeanVirtualsize'] = 0
            results['SectionsMinVirtualsize'] = 0
            results['SectionMaxVirtualsize'] = 0
        else:
            entropy = list(map(lambda x: x.get_entropy(), self.pe.sections))
            results['SectionsMeanEntropy'] = sum(entropy) / float(len(entropy))
            results['SectionsMinEntropy'] = min(entropy)
            results['SectionsMaxEntropy'] = max(entropy)
            raw_sizes = list(map(lambda x: x.SizeOfRawData, self.pe.sections))
            results['SectionsMeanRawsize'] = sum(raw_sizes) / float(len(raw_sizes))
            results['SectionsMinRawsize'] = min(raw_sizes)
            results['SectionsMaxRawsize'] = max(raw_sizes)
            virtual_sizes = list(map(lambda x: x.Misc_VirtualSize, self.pe.sections))
            results['SectionsMeanVirtualsize'] = sum(virtual_sizes) / float(len(virtual_sizes))
            results['SectionsMinVirtualsize'] = min(virtual_sizes)
            results['SectionMaxVirtualsize'] = max(virtual_sizes)

        # Imports
        try:
            results['ImportsNbDLL'] = len(self.pe.DIRECTORY_ENTRY_IMPORT)
            imports = sum([x.imports for x in self.pe.DIRECTORY_ENTRY_IMPORT], [])
            results['ImportsNb'] = len(imports)
            results['ImportsNbOrdinal'] = len(list(filter(lambda x: x.name is None, imports)))
        except AttributeError:
            results['ImportsNbDLL'] = 0
            results['ImportsNb'] = 0
            results['ImportsNbOrdinal'] = 0

        # Exports
        try:
            results['ExportNb'] = len(self.pe.DIRECTORY_ENTRY_EXPORT.symbols)
        except AttributeError:
            results['ExportNb'] = 0

        # Resources
        resources = self.resources()
        results['ResourcesNb'] = len(resources)
        if len(resources) > 0:
            entropy = list(map(lambda x: x[0], resources))
            results['ResourcesMeanEntropy'] = sum(entropy) / float(len(entropy))
            results['ResourcesMinEntropy'] = min(entropy)
            results['ResourcesMaxEntropy'] = max(entropy)
            sizes = list(map(lambda x: x[1], resources))
            results['ResourcesMeanSize'] = sum(sizes) / float(len(sizes))
            results['ResourcesMinSize'] = min(sizes)
            results['ResourcesMaxSize'] = max(sizes)
        else:
            results['ResourcesNb'] = 0
            results['ResourcesMeanEntropy'] = 0
            results['ResourcesMinEntropy'] = 0
            results['ResourcesMaxEntropy'] = 0
            results['ResourcesMeanSize'] = 0
            results['ResourcesMinSize'] = 0
            results['ResourcesMaxSize'] = 0

        # Load configuration size
        try:
            results['LoadConfigurationSize'] = self.pe.DIRECTORY_ENTRY_LOAD_CONFIG.struct.Size
        except AttributeError:
            results['LoadConfigurationSize'] = 0

        # Version configuration size
        try:
            results['flags'] = self.pe.VS_FIXEDFILEINFO.FileFlags
            results['os'] = self.pe.VS_FIXEDFILEINFO.FileOS
            results['type'] = self.pe.VS_FIXEDFILEINFO.FileType
            results['file_version'] = self.pe.VS_FIXEDFILEINFO.FileVersionLS
            results['product_version'] = self.pe.VS_FIXEDFILEINFO.ProductVersionLS
            results['struct_version'] = self.pe.VS_FIXEDFILEINFO.StrucVersion
        except AttributeError:
            results['flags'] = 0
            results['os'] = 0
            results['type'] = 0
            results['file_version'] = 0
            results['product_version'] = 0
            results['struct_version'] = 0
        return results


if __name__ == "__main__":

    for x in range(1):
        start = time.time()
        pe = PortableExecutable("F:/Ungrd-Research/analyzer/Server/uploaded/FingerPassServer (1).exe")
        results = pe.run()
        end = time.time()
        print("\nElapsed time: ", end - start)

    for r in results:
        print(r," : ", results[r])

