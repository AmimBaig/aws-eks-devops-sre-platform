{{- define "opentelemetry-collector.name" -}}
{{- .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "opentelemetry-collector.fullname" -}}
{{- printf "%s-%s" .Release.Name (include "opentelemetry-collector.name" .) | trunc 63 | trimSuffix "-" }}
{{- end }}
