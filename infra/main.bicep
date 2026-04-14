// ============================================================================
// CTF-Marzo2  –  Azure VM running all CTF challenges via Docker Compose
// VM Size: Standard_B2as_v2 (2 vCPUs, 8 GB RAM, burstable) in Canada Central
//
// Pre-requisite: upload tarball to Azure Blob Storage
//   tar czf ctf-marzo2.tar.gz --exclude='.git' .
//   az storage blob upload --account-name ctfmarzo2sa --container-name deploy \
//     --name ctf-marzo2.tar.gz --file ctf-marzo2.tar.gz --overwrite
//
// Deploy:
//   az deployment group create \
//     --resource-group ctf-marzo2-rg \
//     --template-file infra/main.bicep \
//     --parameters adminUsername=ctfadmin \
//                  adminPasswordOrKey='<your-password>'
// ============================================================================

@description('Admin username for the VM')
param adminUsername string = 'ctfadmin'

@description('SSH public key or password for VM access')
@secure()
param adminPasswordOrKey string

@description('Authentication type: sshPublicKey or password')
@allowed(['sshPublicKey', 'password'])
param authenticationType string = 'password'

@description('URL of the CTF tarball in Azure Blob Storage')
param tarballUrl string = 'https://ctfmarzo2sa.blob.core.windows.net/deploy/ctf-marzo2.tar.gz'

@description('Location for all resources')
param location string = 'canadacentral'

@description('VM size – 2 vCPUs, 8 GB RAM (burstable)')
param vmSize string = 'Standard_B2as_v2'

// ---------------------------------------------------------------------------
// Variables
// ---------------------------------------------------------------------------
var vmName = 'ctf-marzo2-vm'
var nicName = '${vmName}-nic'
var nsgName = '${vmName}-nsg'
var vnetName = '${vmName}-vnet'
var subnetName = 'default'
var publicIpName = '${vmName}-pip'
var osDiskName = '${vmName}-osdisk'

var linuxConfiguration = {
  disablePasswordAuthentication: true
  ssh: {
    publicKeys: [
      {
        path: '/home/${adminUsername}/.ssh/authorized_keys'
        keyData: adminPasswordOrKey
      }
    ]
  }
}

// Cloud-init script – installs Docker, downloads tarball, starts docker compose
var cloudInitPart1 = '''
#cloud-config
package_update: true
package_upgrade: true

packages:
  - apt-transport-https
  - ca-certificates
  - curl
  - gnupg
  - lsb-release

runcmd:
  # Install Docker
  - curl -fsSL https://get.docker.com | sh
  - systemctl enable docker
  - systemctl start docker

  # Download and extract CTF tarball
  - mkdir -p /opt/ctf-marzo2
  - curl -fsSL '''

var cloudInitPart2 = ''' -o /tmp/ctf-marzo2.tar.gz
  - tar xzf /tmp/ctf-marzo2.tar.gz -C /opt/ctf-marzo2
  - rm /tmp/ctf-marzo2.tar.gz

  # Start all challenges with docker compose
  - cd /opt/ctf-marzo2 && docker compose up -d --build
'''

var cloudInit = '${cloudInitPart1}${tarballUrl}${cloudInitPart2}'

// ---------------------------------------------------------------------------
// Public IP
// ---------------------------------------------------------------------------
resource publicIp 'Microsoft.Network/publicIPAddresses@2023-11-01' = {
  name: publicIpName
  location: location
  sku: { name: 'Standard' }
  properties: {
    publicIPAllocationMethod: 'Static'
    publicIPAddressVersion: 'IPv4'
  }
}

// ---------------------------------------------------------------------------
// NSG – allow SSH + challenge ports 8001-8005
// ---------------------------------------------------------------------------
resource nsg 'Microsoft.Network/networkSecurityGroups@2023-11-01' = {
  name: nsgName
  location: location
  properties: {
    securityRules: [
      {
        name: 'Allow-SSH'
        properties: {
          priority: 1000
          direction: 'Inbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRange: '22'
          sourceAddressPrefix: '*'
          destinationAddressPrefix: '*'
        }
      }
      {
        name: 'Allow-CTF-Ports'
        properties: {
          priority: 1100
          direction: 'Inbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRange: '8001-8010'
          sourceAddressPrefix: '*'
          destinationAddressPrefix: '*'
        }
      }
    ]
  }
}

// ---------------------------------------------------------------------------
// Virtual Network + Subnet
// ---------------------------------------------------------------------------
resource vnet 'Microsoft.Network/virtualNetworks@2023-11-01' = {
  name: vnetName
  location: location
  properties: {
    addressSpace: { addressPrefixes: ['10.0.0.0/16'] }
    subnets: [
      {
        name: subnetName
        properties: {
          addressPrefix: '10.0.0.0/24'
          networkSecurityGroup: { id: nsg.id }
        }
      }
    ]
  }
}

// ---------------------------------------------------------------------------
// NIC
// ---------------------------------------------------------------------------
resource nic 'Microsoft.Network/networkInterfaces@2023-11-01' = {
  name: nicName
  location: location
  properties: {
    ipConfigurations: [
      {
        name: 'ipconfig1'
        properties: {
          subnet: { id: '${vnet.id}/subnets/${subnetName}' }
          publicIPAddress: { id: publicIp.id }
          privateIPAllocationMethod: 'Dynamic'
        }
      }
    ]
  }
}

// ---------------------------------------------------------------------------
// Virtual Machine
// ---------------------------------------------------------------------------
resource vm 'Microsoft.Compute/virtualMachines@2024-03-01' = {
  name: vmName
  location: location
  properties: {
    hardwareProfile: { vmSize: vmSize }
    osProfile: {
      computerName: vmName
      adminUsername: adminUsername
      adminPassword: authenticationType == 'password' ? adminPasswordOrKey : null
      linuxConfiguration: authenticationType == 'sshPublicKey' ? linuxConfiguration : null
      customData: base64(cloudInit)
    }
    storageProfile: {
      osDisk: {
        name: osDiskName
        createOption: 'FromImage'
        managedDisk: { storageAccountType: 'Premium_LRS' }
        diskSizeGB: 30
      }
      imageReference: {
        publisher: 'Canonical'
        offer: '0001-com-ubuntu-server-jammy'
        sku: '22_04-lts-gen2'
        version: 'latest'
      }
    }
    networkProfile: {
      networkInterfaces: [{ id: nic.id }]
    }
    diagnosticsProfile: {
      bootDiagnostics: { enabled: true }
    }
  }
}

// ---------------------------------------------------------------------------
// Outputs
// ---------------------------------------------------------------------------
output vmPublicIp string = publicIp.properties.ipAddress
output sshCommand string = 'ssh ${adminUsername}@${publicIp.properties.ipAddress}'
output challengeUrls object = {
  crypto_lcg: 'nc ${publicIp.properties.ipAddress} 8001'
  crypto_nebulachat: 'nc ${publicIp.properties.ipAddress} 8009'
  crypto_mersenne: 'nc ${publicIp.properties.ipAddress} 8010'
  web_jwt_confusion: 'http://${publicIp.properties.ipAddress}:8002'
  web_pkl_injection: 'http://${publicIp.properties.ipAddress}:8003'
  web_xss: 'http://${publicIp.properties.ipAddress}:8004'
  web_xxe: 'http://${publicIp.properties.ipAddress}:8005'
  web1_research_portal: 'http://${publicIp.properties.ipAddress}:8006'
  web2_link_checker: 'http://${publicIp.properties.ipAddress}:8007'
  misc1_neural_guard: 'nc ${publicIp.properties.ipAddress} 8008'
}
