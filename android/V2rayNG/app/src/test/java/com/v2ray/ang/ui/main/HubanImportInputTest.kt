package com.v2ray.ang.ui.main

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Test

class HubanImportInputTest {
    @Test fun `empty import requires a useful validation message`() {
        assertEquals(HubanImportProblem.EMPTY, hubanImportProblem("  \n "))
    }

    @Test fun `subscription URL must have a host`() {
        assertEquals(HubanImportProblem.INVALID_URL, hubanImportProblem("https://"))
        assertEquals(HubanImportProblem.INVALID_URL, hubanImportProblem("https://bad host/sub"))
        assertNull(hubanImportProblem("https://example.org/sub?token=private"))
        assertNull(hubanImportProblem("http://10.0.2.2:8765/sub"))
    }

    @Test fun `share links JSON and base64 remain owned by protocol parsers`() {
        assertNull(hubanImportProblem("vless://id@example.org:443#node"))
        assertNull(hubanImportProblem("{\"outbounds\":[]}"))
        assertNull(hubanImportProblem("dmxlc3M6Ly9leGFtcGxl"))
    }
}
