==============
Access Control
==============

This module allows to manage users' rights using profiles.

Odoo's groups are a coherent set of rules that functionally consistent. Profiles allow you to combine several groups and effectively tailor users' access to each user.

Here an exemple :

* accounting group : create an invoice, modify an invoice, cancel an invoice
* business develloper group : create a lead, modify data of lead, close a deal

The CEO of an SME will probably belong to both groups. Profils allows to combine the both groups in one profil.

This is an alternative way to manage users rights by functional profiles.

Basically, a « profile » is a fictive user (res.users) tagged as a profile.

It means that like before (with the basic rules of Odoo),
you can add groups to your profile.

Features:

* You can associate a profile to created users.
* You can add users by profile.
* You can set fields to update for linked users.
* You have the choice to update or not in write mode for associated users,
  with field 'Update users' in profiles.

**Table of contents**

.. contents::
   :local:

Configuration
=============

To configure this module, you need to:

* Go to new menu **Settings > Users & Companies > User Profiles** and create the
  profiles you need.

Usage
=====

* Go to new menu **Settings > Users & Companies > Users** and create a new
  user, choose the profile and after saving you will have user access rights set.

