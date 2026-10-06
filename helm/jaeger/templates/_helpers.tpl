{{- define "jaeger.name" -}}
{{- .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "jaeger.fullname" -}}
{{- printf "%s-%s" .Release.Name (include "jaeger.name" .) | trunc 63 | trimSuffix "-" }}
{{- end }}
