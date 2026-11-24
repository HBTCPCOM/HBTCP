package com.v2ray.ang.ui.main

import java.net.URI

internal enum class HbtcpImportProblem { EMPTY, INVALID_URL }

/** Only validates the entry boundary; the existing protocol parsers remain authoritative. */
internal fun hbtcpImportProblem(text: String): HbtcpImportProblem? {
    val input = text.trim()
    if (input.isEmpty()) return HbtcpImportProblem.EMPTY
    if (input.startsWith("http://", ignoreCase = true) ||
        input.startsWith("https://", ignoreCase = true)
    ) {
        val uri = runCatching { URI(input) }.getOrNull()
        if (uri?.host.isNullOrEmpty()) return HbtcpImportProblem.INVALID_URL
    }
    return null
}
