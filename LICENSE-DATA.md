# Data licence and attributions

The 3D models and anatomy data in this repository are licensed under the
**Creative Commons Attribution-ShareAlike 4.0 International** licence
(<https://creativecommons.org/licenses/by-sa/4.0/>).

If you share or adapt them, you must credit the sources below and release your
version under the same licence.

## Files covered

- `app/anatomy.txt`, `app/manifest.json`: standard mesh pack
- `app/hd.json`, `app/hd5.txt` to `app/hd8.txt`: HD mesh pack
- `app/nerves.json`, `app/vessels.json`: nerve and vessel paths
- `app/defs.json`: "About" text for each structure
- `docs/*.png`: screenshots of the above

## Sources

| Source | Used for | Licence |
|---|---|---|
| **Z-Anatomy**: The libre 3D atlas of anatomy, by Gauthier Kervyn, Marcin Zielinski, Lluis Vinent and contributors. <https://www.z-anatomy.com> | Muscle, bone, ligament, nerve and vessel models; structure definitions | CC BY-SA 4.0 |
| **BodyParts3D**, © The Database Center for Life Science (DBCLS), Kousaku Okubo. <https://dbarchive.biosciencedbc.jp/en/bodyparts3d/> | Underlying scan geometry (the source of Z-Anatomy, and the large trunk vessels and heart used directly) | CC BY-SA 2.1 Japan |
| **Wikipedia** contributors, via Z-Anatomy | "About" text in `defs.json`, adapted and shortened | CC BY-SA 3.0 / 4.0 |

Z-Anatomy's own attributions also apply to the parts of its atlas used here.
These include "Cranial Nerves and Foramina" (University of Dundee, CAHID, CC BY 4.0).

## Changes made

The meshes were extracted from the Z-Anatomy Blender file, aligned to the
BodyParts3D coordinate frame, subdivided and simplified, and repackaged. Some
ligaments missing from Z-Anatomy were modelled as bands between landmarks on
these bones. A few nerves and vessels were traced by hand.

## Not covered by this file

- Course notes in `app/content.json` (origins, insertions, actions,
  innervations, mnemonics and bellringer cases) were written for this project
  and are released under CC BY-SA 4.0 as well.
- `app/eng.txt` is the Tesseract English language model (Apache 2.0).
- `app/lib/` contains three.js r147 (MIT, © three.js authors).
