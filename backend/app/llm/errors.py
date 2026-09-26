class LLMError(RuntimeError): pass
class LLMConfigurationError(LLMError): pass
class LLMTimeoutError(LLMError): pass
class LLMAuthenticationError(LLMError): pass
class LLMRateLimitError(LLMError): pass
class LLMUpstreamError(LLMError): pass
class LLMInvalidResponseError(LLMError): pass
