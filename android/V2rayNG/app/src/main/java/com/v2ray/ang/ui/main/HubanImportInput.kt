package com.v2ray.ang.ui.main

import java.net.URI

internal enum class HubanImportProblem { EMPTY, INVALID_URL }

/** Only validates the entry boundary; the existing protocol parsers remain authoritative. */
internal fun hubanImportProblem(text: String): HubanImportProblem? {
    val input = text.trim()
    if (input.isEmpty()) return HubanImportProblem.EMPTY
    if (input.startsWith("http://", ignoreCase = true) ||
        input.startsWith("https://", ignoreCase = true)
    ) {
        val uri = runCatching { URI(input) }.getOrNull()
        if (uri?.host.isNullOrEmpty()) return HubanImportProblem.INVALID_URL
    }
    return null
}
