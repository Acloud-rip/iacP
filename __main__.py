import pulumi
from pulumi_gcp import compute
import pulumi_gcp as gcp

# Crear una red VPC en dev sin etiquetas
vpc = compute.Network("dev-vpc-southamerica-west1", auto_create_subnetworks=False)

# Crear una subred en la VPC en dev sin etiquetas
subnet = compute.Subnetwork("dev-subnet-southamerica-west1",
    ip_cidr_range="10.0.0.0/24",
    region="southamerica-west1",
    network=vpc.id
)

# Crear una regla de firewall para permitir SSH en dev sin etiquetas
firewall = compute.Firewall("allow-ssh-dev",
    network=vpc.id,
    allows=[{
        "protocol": "tcp",
        "ports": ["22"],
    }],
    source_ranges=["0.0.0.0/0"],  # Permitir desde cualquier IP (no recomendado en producción)
)

# Crear una instancia de máquina virtual en dev
instance = compute.Instance("dev-instance",
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
    }],
    labels={"env": "dev", "owner": "team_rip_gcp", "purpose": "web-server"}
)

# Crear un clúster GKE en dev
cluster = gcp.container.Cluster("dev-gke-cluster",
    initial_node_count=1,
    deletion_protection=False,  # Desactiva la protección contra eliminación
    node_config=gcp.container.ClusterNodeConfigArgs(
        machine_type="e2-medium",  # Especifica el tipo de máquina
        oauth_scopes=[
            "https://www.googleapis.com/auth/cloud-platform",
        ],
    ),
    location="southamerica-west1-a",  # Región deseada
    
)

# Exportar información útil
pulumi.export("instance_name", instance.name)
pulumi.export("instance_ip", instance.network_interfaces[0].access_configs[0].nat_ip)
pulumi.export("cluster_name", cluster.name)
pulumi.export("cluster_location", cluster.location)
