# Privacy audit

## Changes made

- Updated `/privacy/` to describe both inquiry forms, their submitted fields, the generated submission timestamp, the project-inquiry anti-spam field, portal account/project data, and access boundaries.
- Clarified that application records are stored in the configured database and that the hosting/database providers process information needed to operate the service. Passwords are handled by Django authentication as hashes.
- Documented Django session and CSRF cookies and the legacy browser-side `eddyforge_content_override` local-storage value. No authentication use of `sessionStorage` remains.
- Confirmed there is no analytics integration in the application source.
- Listed the external asset providers: Google Fonts (`fonts.googleapis.com` and Google-hosted font files), jsDelivr (`cdn.jsdelivr.net`), and cdnjs (`cdnjs.cloudflare.com`). Also described links to WhatsApp, GitHub, LinkedIn, optional booking-page embedding, and externally configured project URLs/images.
- Described retention accurately as operator-controlled because the project does not implement an automatic retention/deletion schedule.

## Open questions for the site owner

- What retention period should apply to inquiry, portal, and project records?
- What legal/controller name should this notice identify?
- What contact email should appear as the privacy contact?

## Required owner review

Check whether registration with Kenya's Office of the Data Protection Commissioner (ODPC) is required for the actual operation, and obtain a legal review before launch. This audit and notice do not assert compliance with any law.
