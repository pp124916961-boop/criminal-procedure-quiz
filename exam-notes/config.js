// 考試筆記共用設定
// 之後任何科目新增一般 JPG，只需要：
// 1. 把圖片依序放進該科 directory，檔名 page-01.jpg、page-02.jpg...
// 2. 只修改該科的 total
// 首頁頁數、滑桿、翻頁、放大、預載都會自動同步。
window.EXAM_NOTES_CONFIG = Object.freeze({
  order: Object.freeze([
    'constitution',
    'policeLaw',
    'policeDuty',
    'criminalProcedure',
    'criminalLaw',
    'admin'
  ]),
  subjects: Object.freeze({
    constitution: Object.freeze({
      name: '憲法',
      total: 0,
      directory: 'assets/constitution',
      prefix: 'page-',
      defaultExtension: 'jpg',
      overrides: Object.freeze({})
    }),
    policeLaw: Object.freeze({
      name: '警察法規',
      total: 0,
      directory: 'assets/police-law',
      prefix: 'page-',
      defaultExtension: 'jpg',
      overrides: Object.freeze({})
    }),
    policeDuty: Object.freeze({
      name: '警察勤務',
      total: 78,
      directory: 'assets/police-duty',
      prefix: 'page-',
      defaultExtension: 'jpg',
      overrides: Object.freeze({})
    }),
    criminalProcedure: Object.freeze({
      name: '刑事訴訟法',
      total: 97,
      directory: 'assets/criminal-procedure',
      prefix: 'page-',
      defaultExtension: 'jpg',
      overrides: Object.freeze({})
    }),
    criminalLaw: Object.freeze({
      name: '刑法',
      total: 98,
      directory: 'assets/criminal-law',
      prefix: 'page-',
      defaultExtension: 'jpg',
      overrides: Object.freeze({})
    }),
    admin: Object.freeze({
      name: '行政法',
      total: 52,
      directory: 'assets/admin-pages',
      prefix: 'page-',
      defaultExtension: 'jpg',
      // 只有不是一般 JPG 的特殊頁面才需要列在這裡。
      overrides: Object.freeze({
        51: 'page-51.svg'
      })
    })
  })
});
