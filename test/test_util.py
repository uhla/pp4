from scripts.util import util


def test_describe_changelist1():
    describe = "Change 849796 by dusan.jakub@dusan.jakub_dusan-devbox2_--n-central-11.1-SP1-HF1-withGoogle_-home-dusan-Projects-n-central-11.1-SP1-HF1-withGoogle-Workspace on 2017/12/08 06:37:48\n" + \
               "\n" + \
               "\tRename GoogleUsers SQL file from 730-vNext.sql to 741-11_1_SP1_HF1.sql\n" + \
               "\n" + \
               "Affected files ...\n" + \
               "\n" + \
               "... //n-central/11.1-SP1-HF1-withGoogle/dms/database/sql/Patch/Post/730-vNext.sql#5 move/delete\n" + \
               "... //n-central/11.1-SP1-HF1-withGoogle/dms/database/sql/Patch/Post/741-11_1_SP1_HF1.sql#1 move/add\n" + \
               "\n" + \
               "\n"

    cl = util.parse_describe_changelist(describe)
    assert cl.number == "849796"
    assert cl.user == "dusan.jakub"
    assert cl.workspace == "dusan.jakub_dusan-devbox2_--n-central-11.1-SP1-HF1-withGoogle_-home-dusan-Projects-n-central-11.1-SP1-HF1-withGoogle-Workspace"
    assert cl.datestr == "2017/12/08 06:37:48"
    assert cl.description == "Rename GoogleUsers SQL file from 730-vNext.sql to 741-11_1_SP1_HF1.sql"
    assert cl.affected_files == [
        ("//n-central/11.1-SP1-HF1-withGoogle/dms/database/sql/Patch/Post/730-vNext.sql", "5", "move/delete"),
        ("//n-central/11.1-SP1-HF1-withGoogle/dms/database/sql/Patch/Post/741-11_1_SP1_HF1.sql", "1", "move/add")
    ]
    assert cl.stream == ["//n-central/11.1-SP1-HF1-withGoogle"]
    assert not cl.pending


def test_describe_changelist2():
    describe = "Change 842755 by dusan.jakub@dusan.jakub_dusan-devbox2_--n-central-dev-vNext_-home-dusan-Projects-n-central-dev-vNext-Workspace on 2017/09/26 10:46:21 *pending*\n" + \
               "\n" + \
               "\tNPSA-4740: ConnectWise failure to create tickets\n" + \
               "\n" + \
               "Affected files ...\n" + \
               "\n" + \
               "\n"

    cl = util.parse_describe_changelist(describe)
    assert cl.number == "842755"
    assert cl.user == "dusan.jakub"
    assert cl.workspace == "dusan.jakub_dusan-devbox2_--n-central-dev-vNext_-home-dusan-Projects-n-central-dev-vNext-Workspace"
    assert cl.datestr == "2017/09/26 10:46:21"
    assert cl.description == "NPSA-4740: ConnectWise failure to create tickets"
    assert cl.affected_files == []
    assert cl.stream == []
    assert cl.pending

def test_describe_changelist3():
    describe = "Change 842755 by dusan.jakub@dusan.jakub_dusan-devbox2_--n-central-dev-vNext_-home-dusan-Projects-n-central-dev-vNext-Workspace on 2017/09/26 10:46:21 *pending*\n" + \
               "\n" + \
               "\tNPSA-4740: ConnectWise failure to create tickets\n" + \
               "\n" + \
               "Affected files ...\n" + \
               "\n" + \
               "... //n-central/dev-vNext/ui/ui/dojoroot/xtnd/device/templates/updateTicketAssigneeSectionSingle.html#none add\n" + \
               "\n" + \
               "Differences ...\n" + \
               "\n" + \
               "@@ -25,8 +25,16 @@\n" + \
               "     private boolean hdmCcGroupManager;\n" + \
               "     private String hdmCcList;\n" + \
               "     private String hdmBccList;\n" + \
               "     private boolean publicNote;\n" + \
               "+    private List<String> assignedTechIds;\n" + \
               "\n" + \
               "     public String getTicketNumber() {\n" + \
               "         return ticketNumber;\n" + \
               "     }\n" + \
               "\n"

    cl = util.parse_describe_changelist(describe)
    assert cl.number == "842755"
    assert cl.user == "dusan.jakub"
    assert cl.workspace == "dusan.jakub_dusan-devbox2_--n-central-dev-vNext_-home-dusan-Projects-n-central-dev-vNext-Workspace"
    assert cl.datestr == "2017/09/26 10:46:21"
    assert cl.description == "NPSA-4740: ConnectWise failure to create tickets"
    assert cl.affected_files == [
        ("//n-central/dev-vNext/ui/ui/dojoroot/xtnd/device/templates/updateTicketAssigneeSectionSingle.html", "none", "add")]
    assert cl.stream == ["//n-central/dev-vNext"]
    assert cl.pending
    assert cl.differences
