import pulumi
from pulumi_gcp import compute

# Crear una red VPC
vpc = compute.Network("my-vpc", auto_create_subnetworks=False)

# Crear una subred en la VPC
subnet = compute.Subnetwork("my-subnet",
    ip_cidr_range="10.0.0.0/24",
    region="southamerica-west1",
    network=vpc.id)

# Crear una regla de firewall para permitir SSH
firewall = compute.Firewall("allow-ssh",
    network=vpc.id,
    allows=[{
        "protocol": "tcp",
        "ports": ["22"],
    }],
    source_ranges=["0.0.0.0/0"])  # Permitir desde cualquier IP (no recomendado en producción)

# Crear una instancia de máquina virtual
instance = compute.Instance("my-instance",
    machine_type="e2-micro",
    zone="southamerica-west1-a",
    boot_disk={
        "initializeParams": {
            "image": "debian-cloud/debian-11",
        },
    },
    network_interfaces=[{
        "network": vpc.id,
        "subnetwork": subnet.id,
        "accessConfigs": [{}],  # Esto asigna una IP pública
    }])

# Exportar información útil
pulumi.export("instance_name", instance.name)
pulumi.export("instance_ip", instance.network_interfaces[0].access_configs[0].nat_ip)