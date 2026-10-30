"""The parsing rules of the CogniCrypt side: method names, budgets, rejected rules."""

import re

import pytest

from scripts.cognicrypt import BUDGET
from scripts.venn import METHOD_NAME, REJECTED


@pytest.mark.parametrize("signature, name", [
    ("<a.B: void <init>(java.lang.String)>", "<init>"),
    ("<a.B: void <clinit>()>", "<clinit>"),
    ("<a.B: javax.net.ssl.X509TrustManager platformTrustManager()>", "platformTrustManager"),
    ("<a.B$C: byte[] do$it(byte[],int)>", "do$it"),
])
def test_method_name(signature, name):
    assert re.search(METHOD_NAME, signature).group(1) == name


def test_budget():
    assert re.match(BUDGET, "2x40g/3600s").groupdict() == {"attempts": "2", "heap": "40",
                                                           "secs": "3600"}
    assert re.match(BUDGET, "2x40g/3600") is None


def test_rejected_rule_crosses_anonymized_path():
    msg = "Skipping rule since it contains errors: <WORKSPACE>/rules/SSLEngine.crysl"
    assert re.findall(REJECTED, msg) == ["SSLEngine"]
