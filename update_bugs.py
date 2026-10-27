with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update parseLocalDate
old_parse_local = '''function parseLocalDate(dateStr) {
  if (!dateStr || typeof dateStr !== 'string') return null;
  const parts = dateStr.split('-').map(Number);
  if (parts.length === 3 && !parts.some(isNaN)) {
    return new Date(parts[0], parts[1] - 1, parts[2]);
  }
  const d = new Date(dateStr);
  return isNaN(d.getTime()) ? null : d;
}'''

new_parse_local = '''function parseLocalDate(dateStr) {
  if (!dateStr || typeof dateStr !== 'string') return null;
  const parts = dateStr.trim().split(/[\\/\\-]/).map(Number);
  if (parts.length === 3 && !parts.some(isNaN)) {
    let year, month, day;
    if (parts[0] > 31) { // YYYY-MM-DD or YYYY/MM/DD
      year = parts[0]; month = parts[1] - 1; day = parts[2];
    } else if (parts[2] > 31) { // DD/MM/YYYY or DD-MM-YYYY
      day = parts[0]; month = parts[1] - 1; year = parts[2];
    } else {
      year = parts[0]; month = parts[1] - 1; day = parts[2];
    }
    return new Date(year, month, day);
  }
  const d = new Date(dateStr);
  return isNaN(d.getTime()) ? null : d;
}'''

assert old_parse_local in content, 'old_parse_local not found'
content = content.replace(old_parse_local, new_parse_local, 1)

# 2. Update saveEditClass
old_save_edit_class = '''function saveEditClass(idx) {
  const input = document.getElementById(`class-edit-${idx}`);
  const newName = input.value.trim();
  const oldName = tempClasses[idx].name;

  if (!newName) { toast('Nama kelas tidak boleh kosong!', 'error'); return; }
  if (newName.length > 30) { toast('Maksimal 30 karakter!', 'error'); return; }
  if (tempClasses.some((c, i) => i !== idx && c.name.toLowerCase() === newName.toLowerCase())) {
    toast(`Nama kelas "${newName}" sudah ada!`, 'error'); return;
  }
  tempClasses[idx].name = newName;
  renderClassList();
  toast(`✅ "${oldName}" diperbarui`);
}'''

new_save_edit_class = '''function saveEditClass(idx) {
  const input = document.getElementById(`class-edit-${idx}`);
  const newName = input.value.trim();
  const oldName = tempClasses[idx].name;

  if (!newName) { toast('Nama kelas tidak boleh kosong!', 'error'); return; }
  if (newName.length > 30) { toast('Maksimal 30 karakter!', 'error'); return; }
  if (tempClasses.some((c, i) => i !== idx && c.name.toLowerCase() === newName.toLowerCase())) {
    toast(`Nama kelas "${newName}" sudah ada!`, 'error'); return;
  }
  tempClasses[idx].name = newName;
  if (tempTeacherSchedule && tempTeacherSchedule.length > 0) {
    tempTeacherSchedule.forEach(ts => {
      if (ts.className === oldName) ts.className = newName;
    });
  }
  renderClassList();
  renderTeacherScheduleList();
  toast(`✅ "${oldName}" diperbarui`);
}'''

assert old_save_edit_class in content, 'old_save_edit_class not found'
content = content.replace(old_save_edit_class, new_save_edit_class, 1)

# 3. Update removeClass
old_remove_class = '''  showConfirm('🗑 Hapus Kelas', warnMsg + '\\n\\nTindakan ini tidak bisa dibatalkan.', () => {
    const wasActive = idx === currentClass;
    tempClasses.splice(idx, 1);
    if (wasActive) {
      currentClass = 0;
      currentMeeting = 1;
    } else if (idx < currentClass) {
      currentClass--;
    }
    renderClassList();
    toast(`✅ Kelas "${cls.name}" dihapus`);
  }, false);'''

new_remove_class = '''  showConfirm('🗑 Hapus Kelas', warnMsg + '\\n\\nTindakan ini tidak bisa dibatalkan.', () => {
    const wasActive = idx === currentClass;
    const removedName = cls.name;
    tempClasses.splice(idx, 1);
    if (tempTeacherSchedule && tempTeacherSchedule.length > 0) {
      tempTeacherSchedule = tempTeacherSchedule.filter(ts => ts.className !== removedName);
    }
    if (wasActive) {
      currentClass = 0;
      currentMeeting = 1;
    } else if (idx < currentClass) {
      currentClass--;
    }
    renderClassList();
    renderTeacherScheduleList();
    toast(`✅ Kelas "${removedName}" dihapus`);
  }, false);'''

assert old_remove_class in content, 'old_remove_class not found'
content = content.replace(old_remove_class, new_remove_class, 1)

# 4. Update findOrCreateClassByName to ignore non-class sheet names
old_find_class = '''function findOrCreateClassByName(rawClassName) {
  const name = String(rawClassName || '').trim();
  if (!name) return currentClass;
  let idx = state.classes.findIndex(c => c.name.toLowerCase() === name.toLowerCase());
  if (idx >= 0) return idx;

  const num = parseInt(name.replace(/[^0-9]/g, ''));
  if (!isNaN(num) && num >= 1 && num <= state.classes.length) {
    return num - 1;
  }

  const newClass = {
    id: 'c_' + Date.now() + '_' + Math.random().toString(36).slice(2, 6),
    name: name,
    subject: (state.subjects && state.subjects[0]) || 'Informatika',
    students: [],
    attendance: {},
    meetings: 0,
    meetingsData: {},
    startHour: 1,
    endHour: 3
  };
  state.classes.push(newClass);
  return state.classes.length - 1;
}'''

new_find_class = '''function findOrCreateClassByName(rawClassName) {
  const name = String(rawClassName || '').trim();
  if (!name) return currentClass;
  if (/^sheet\\d*$/i.test(name) || /^info/i.test(name) || /materi$/i.test(name) || /^template/i.test(name)) {
    return currentClass;
  }
  let idx = state.classes.findIndex(c => c.name.toLowerCase() === name.toLowerCase());
  if (idx >= 0) return idx;

  const num = parseInt(name.replace(/[^0-9]/g, ''));
  if (!isNaN(num) && num >= 1 && num <= state.classes.length) {
    return num - 1;
  }

  const newClass = {
    id: 'c_' + Date.now() + '_' + Math.random().toString(36).slice(2, 6),
    name: name,
    subject: (state.subjects && state.subjects[0]) || 'Informatika',
    students: [],
    attendance: {},
    meetings: 0,
    meetingsData: {},
    startHour: 1,
    endHour: 3
  };
  state.classes.push(newClass);
  return state.classes.length - 1;
}'''

assert old_find_class in content, 'old_find_class not found'
content = content.replace(old_find_class, new_find_class, 1)

# 5. Update autoSelectTodayClass so it doesn't overwrite saved meeting hours
old_auto_select = '''    if (targetCls.meetings > 0 && targetCls.meetingsData) {
      if (!targetCls.meetingsData[currentMeeting]) {
        targetCls.meetingsData[currentMeeting] = { date: getLocalDateString(), hour: targetHour, material: '' };
      } else {
        targetCls.meetingsData[currentMeeting].hour = targetHour;
      }
    }'''

new_auto_select = '''    if (targetCls.meetings > 0 && targetCls.meetingsData) {
      if (!targetCls.meetingsData[currentMeeting]) {
        targetCls.meetingsData[currentMeeting] = { date: getLocalDateString(), hour: targetHour, material: '' };
      } else if (!targetCls.meetingsData[currentMeeting].hour) {
        targetCls.meetingsData[currentMeeting].hour = targetHour;
      }
    }'''

assert old_auto_select in content, 'old_auto_select not found'
content = content.replace(old_auto_select, new_auto_select, 1)

# 6. Update buildRekapHTML schedule time resolution
old_rekap_time = '''    let waktu = '-';
    if (scStart && scEnd) {
      const startTimeFormatted = scStart.start.replace(':', '.');
      const endTimeFormatted = scEnd.end.replace(':', '.');
      waktu = `${startTimeFormatted} - ${endTimeFormatted}`;
    } else if (scStart) {
      const startTimeFormatted = scStart.start.replace(':', '.');
      const endTimeFormatted = scStart.end.replace(':', '.');
      waktu = `${startTimeFormatted} - ${endTimeFormatted}`;
    }'''

new_rekap_time = '''    let waktu = '-';
    if (scStart) {
      const startTimeFormatted = scStart.start.replace(':', '.');
      const endTimeFormatted = scEnd ? scEnd.end.replace(':', '.') : scStart.end.replace(':', '.');
      waktu = `${startTimeFormatted} - ${endTimeFormatted}`;
    }'''

assert old_rekap_time in content, 'old_rekap_time not found'
content = content.replace(old_rekap_time, new_rekap_time, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('All bug fixes applied successfully!')
