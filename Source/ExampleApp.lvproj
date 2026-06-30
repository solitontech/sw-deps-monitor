<?xml version='1.0' encoding='UTF-8'?>
<Project Type="Project" LVVersion="19008000">
	<Property Name="NI.LV.All.SourceOnly" Type="Bool">true</Property>
	<Item Name="My Computer" Type="My Computer">
		<Property Name="server.app.propertiesEnabled" Type="Bool">true</Property>
		<Property Name="server.control.propertiesEnabled" Type="Bool">true</Property>
		<Property Name="server.tcp.enabled" Type="Bool">false</Property>
		<Property Name="server.tcp.port" Type="Int">0</Property>
		<Property Name="server.tcp.serviceName" Type="Str">My Computer/VI Server</Property>
		<Property Name="server.tcp.serviceName.default" Type="Str">My Computer/VI Server</Property>
		<Property Name="server.vi.callsEnabled" Type="Bool">true</Property>
		<Property Name="server.vi.propertiesEnabled" Type="Bool">true</Property>
		<Property Name="specify.custom.address" Type="Bool">false</Property>
		<Item Name="Communication" Type="Folder">
			<Item Name="ABComm.lvlib" Type="Library" URL="../Communication/ABComm/ABComm.lvlib"/>
			<Item Name="ACComm.lvlib" Type="Library" URL="../Communication/ACComm/ACComm.lvlib"/>
		</Item>
		<Item Name="Modules" Type="Folder">
			<Item Name="ModuleA.lvlib" Type="Library" URL="../Modules/ModuleA/ModuleA.lvlib"/>
			<Item Name="ModuleB.lvlib" Type="Library" URL="../Modules/ModuleB/ModuleB.lvlib"/>
			<Item Name="ModuleC.lvlib" Type="Library" URL="../Modules/ModuleC/ModuleC.lvlib"/>
			<Item Name="ModuleD.lvclass" Type="LVClass" URL="../Modules/ModuleD/ModuleD.lvclass"/>
		</Item>
		<Item Name="Utilities" Type="Folder">
			<Item Name="ArrayUtilities.lvlib" Type="Library" URL="../Utilities/ArrayUtilities/ArrayUtilities.lvlib"/>
			<Item Name="FileUtilities.lvlib" Type="Library" URL="../Utilities/FileUtilities/FileUtilities.lvlib"/>
			<Item Name="GraphUtilities.lvclass" Type="LVClass" URL="../Utilities/GraphUtilities/GraphUtilities.lvclass"/>
			<Item Name="StringUtilities.lvlib" Type="Library" URL="../Utilities/StringUtilities/StringUtilities.lvlib"/>
		</Item>
		<Item Name="Dependencies" Type="Dependencies">
			<Item Name="Untitled 1.vi" Type="VI" URL="../Modules/ModuleA/Untitled 1.vi"/>
		</Item>
		<Item Name="Build Specifications" Type="Build"/>
	</Item>
</Project>
