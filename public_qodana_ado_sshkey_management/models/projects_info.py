from dataclasses import dataclass

@dataclass
class ProjectInfo:
    qp_name: str
    qp_id: str
    qp_ssh_pubkey: str = ""
    qp_ssh_keyID: str = ""
    ado_authorizationId: str = ""
    ado_expireDate: str = ""
