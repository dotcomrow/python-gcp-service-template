locals {
  ol_svc_name = "ol-svc"
}

data "external" "ol-svc-image-sha" {
  program = ["${path.module}/scripts/get-image-sha.sh", "svc-${local.ol_svc_name}", "${var.common_project_id}"]
}

resource "google_cloud_run_v2_service" "ol-svc" {
  name     = local.ol_svc_name
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"
  project  = var.project_id

  template {
    volumes {
      name = "a-volume"
      secret {
        secret       = var.bigquery_secret
        default_mode = 292 # 0444
        items {
          version = "1"
          path    = "google.key"
        }
      }
    }
    containers {
      image = "${var.registry_name}/${var.common_project_id}/svc-${local.ol_svc_name}@${data.external.ol-svc-image-sha.result["sha"]}"

      env {
        name  = "SECRET_KEY"
        value = var.python_session_secret
      }

      env {
        name  = "PROJECT_ID"
        value = var.project_id
      }

      env {
        name  = "AUDIENCE"
        value = var.audience
      }

      env {
        name  = "REGION"
        value = var.region
      }

      env {
        name = "DOMAIN"
        value = var.domain
      }

      env {
        name  = "CONTEXT_ROOT"
        value = "${local.ol_svc_name}"
      }

      volume_mounts {
        name = "a-volume"
        mount_path = "/secrets"
      }
    }
  }

  depends_on = [ google_project_iam_member.registry_permissions, google_project_iam_member.secret_manager_grant, data.external.ol-svc-image-sha ]
}

resource "google_cloud_run_service_iam_policy" "noauth-user-profile" {
  location = google_cloud_run_v2_service.ol-svc.location
  project  = google_cloud_run_v2_service.ol-svc.project
  service  = google_cloud_run_v2_service.ol-svc.name

  policy_data = data.google_iam_policy.noauth.policy_data
}
