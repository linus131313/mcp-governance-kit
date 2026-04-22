"""The five illustrative agent configurations (C1–C5) and four
traditional-application comparators (R1–R4) from Table 3 of the paper.

These are the reference fixtures used by the CLI reproduction command
``mcp-gov tcs reference`` and by the unit tests that pin the paper's
numerical claims.
"""

from __future__ import annotations

from mcp_governance_kit.tcs.models import Action, Config, Reach, Tool

CONFIGURATIONS: list[Config] = [
    Config(
        label="C1 Conservative (Claude Desktop + filesystem-read-only)",
        short="C1",
        tools=[Tool(name="filesystem-ro", reach=Reach.LOCAL, action=Action.READ)],
    ),
    Config(
        label="C2 Analyst (Claude Desktop + filesystem + sqlite + fetch)",
        short="C2",
        tools=[
            Tool(name="filesystem", reach=Reach.LOCAL, action=Action.WRITE),
            Tool(name="sqlite", reach=Reach.LOCAL, action=Action.WRITE, third_party=True),
            Tool(name="fetch", reach=Reach.NETWORK, action=Action.READ, third_party=True),
        ],
    ),
    Config(
        label="C3 Developer (Cursor + github + filesystem + shell)",
        short="C3",
        tools=[
            Tool(name="github", reach=Reach.NETWORK, action=Action.WRITE, third_party=True),
            Tool(name="filesystem", reach=Reach.LOCAL, action=Action.WRITE),
            Tool(name="shell", reach=Reach.LOCAL, action=Action.EXECUTE, third_party=True),
        ],
    ),
    Config(
        label="C4 Full-stack (Cursor + github + supabase + aws + fs + shell + docker)",
        short="C4",
        tools=[
            Tool(name="github", reach=Reach.NETWORK, action=Action.WRITE, third_party=True),
            Tool(name="supabase", reach=Reach.NETWORK, action=Action.WRITE, third_party=True),
            Tool(name="aws", reach=Reach.NETWORK, action=Action.EXECUTE, third_party=True),
            Tool(name="filesystem", reach=Reach.LOCAL, action=Action.WRITE),
            Tool(name="shell", reach=Reach.LOCAL, action=Action.EXECUTE, third_party=True),
            Tool(name="docker", reach=Reach.LOCAL, action=Action.EXECUTE, third_party=True),
        ],
    ),
    Config(
        label="C5 Security research (Cursor + nmap + metasploit + fs + shell)",
        short="C5",
        tools=[
            Tool(name="nmap", reach=Reach.NETWORK, action=Action.EXECUTE, third_party=True),
            Tool(name="metasploit", reach=Reach.NETWORK, action=Action.EXECUTE, third_party=True),
            Tool(name="filesystem", reach=Reach.LOCAL, action=Action.WRITE),
            Tool(name="shell", reach=Reach.LOCAL, action=Action.EXECUTE, third_party=True),
        ],
    ),
]


COMPARATORS: list[Config] = [
    Config(
        label="R1 Static website (public, read-only)",
        short="R1",
        tools=[Tool(name="http-read", reach=Reach.NETWORK, action=Action.READ)],
    ),
    Config(
        label="R2 SaaS CRM via SSO",
        short="R2",
        tools=[Tool(name="crm", reach=Reach.NETWORK, action=Action.WRITE, third_party=True)],
    ),
    Config(
        label="R3 DBA tool with shell",
        short="R3",
        tools=[
            Tool(name="db", reach=Reach.NETWORK, action=Action.WRITE),
            Tool(name="shell", reach=Reach.LOCAL, action=Action.EXECUTE),
        ],
    ),
    Config(
        label="R4 Domain-admin workstation (DB write + shell + remote exec + fs)",
        short="R4",
        tools=[
            Tool(name="db-admin", reach=Reach.NETWORK, action=Action.WRITE),
            Tool(name="remote-exec", reach=Reach.NETWORK, action=Action.EXECUTE),
            Tool(name="shell", reach=Reach.LOCAL, action=Action.EXECUTE),
            Tool(name="filesystem", reach=Reach.LOCAL, action=Action.WRITE),
        ],
    ),
]


REFERENCE: list[Config] = CONFIGURATIONS + COMPARATORS
"""All nine reference configurations, in the order they appear in Table 3."""
