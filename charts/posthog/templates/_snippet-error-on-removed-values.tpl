{{/* Checks whether removed variables are in use. */}}
{{- define "snippet.error-on-removed-values" }}
{{- if .Values.certManager }}
    {{- required (printf (include "snippet.error-on-removed-values-template" .) "certManager value has been renamed to cert-manager." "https://posthog.com/docs/self-host/deploy/upgrade-notes#upgrading-from-3xx") nil -}}
{{- else if .Values.beat }}
    {{- required (printf (include "snippet.error-on-removed-values-template" .) "beat deployment has been removed." "https://posthog.com/docs/self-host/deploy/upgrade-notes#upgrading-from-7xx") nil -}}
{{- else if .Values.clickhouseOperator }}
    {{- required (printf (include "snippet.error-on-removed-values-template" .) "clickhouseOperator values are no longer valid." "https://posthog.com/docs/self-host/deploy/upgrade-notes#upgrading-from-9xx") nil -}}
{{- else if or .Values.redis.port .Values.redis.host .Values.redis.password }}
    {{- required (printf (include "snippet.error-on-removed-values-template" .) "redis.port, redis.host and redis.password are no longer valid." "https://posthog.com/docs/self-host/deploy/upgrade-notes#upgrading-from-11xx") nil -}}
{{- else if .Values.clickhouse.host }}
    {{- required (printf (include "snippet.error-on-removed-values-template" .) "clickhouse.host has been moved to externalClickhouse.host" "https://posthog.com/docs/self-host/deploy/upgrade-notes#upgrading-from-13xx") nil -}}
{{- else if .Values.clickhouse.replication }}
    {{- required (printf (include "snippet.error-on-removed-values-template" .) "clickhouse.replication has been removed" "https://posthog.com/docs/self-host/deploy/upgrade-notes#upgrading-from-13xx") nil -}}
{{- end -}}
{{- end -}}

{{- define "snippet.error-on-removed-values-template" }}


==== BREAKING CHANGE ====

%s

Read more on how to update your values.yaml:
%s

=========================

{{ end -}}
