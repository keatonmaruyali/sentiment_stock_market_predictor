import base64
from bs4 import BeautifulSoup
from collections import Counter
from copy import deepcopy
from datetime import datetime
from dateutil.parser import parse
from fuzzywuzzy import fuzz, process
from io import BytesIO
from matplotlib.figure import Figure
import pandas as pd
import re


class FundamentalAnalysis:
    def __init__(self):
        self.stat_types = [
            'balance',
            'operation',
            'income/loss/comprehensive_lo',
            # 'stockholder/redeemable/interests/equity',
            'flow'
        ]

    def scrape(self, urls: list):
        return {
            i: self._find_table_by_type(
                table=BeautifulSoup(
                    open(n, "r", encoding='utf-8').read(),
                    "lxml"),
            )
            for i, n in enumerate(urls)
        }

    def _clean_table(self, table, scale, stmt_type = None):
        stmt_df_by_stmt_type = deepcopy(table)
        stmt_df_by_stmt_type.rename(
            columns={stmt_df_by_stmt_type.columns[0]: 'index'},
            inplace=True,
        )

        for i, ind in enumerate(stmt_df_by_stmt_type['index']):
            stmt_df_by_stmt_type['index'][i] = ' '.join(
                re.sub("[\(\[].*?[\)\]]", "", ind)
                .replace(':', '')
                .replace('/', '')
                .replace('loss', 'income')
                .split()
            )
        dup_index_col = [
            i
            for i, v
            in enumerate(
                stmt_df_by_stmt_type.iloc[:, 0].duplicated().to_list()[:4]
            )
            if v
        ]
        stmt_df_by_stmt_type.drop(
            stmt_df_by_stmt_type.columns[dup_index_col],
            axis=1,
            inplace=True,
        )

        if stmt_type == 'balance':
            prefix = ''
            for i, ind in enumerate(stmt_df_by_stmt_type['index']):
                if ind.split(' ')[0].lower() in ['assets', 'liabilities']:
                    prefix = f'{ind.split(" ")[0].lower().capitalize()}: '
                elif ind.split(' ')[0] == 'Total':
                    prefix = ''

                if ', net' in ind:
                    ind = ' '.join(ind.split(',')[:-1])
                    stmt_df_by_stmt_type['index'][i] = f'{prefix}{ind}'
                else:
                    stmt_df_by_stmt_type['index'][i] = f'{prefix}{ind}'

        if stmt_type == 'operation':
            prefix = ''
            for i, ind in enumerate(stmt_df_by_stmt_type['index']):
                if all(list(stmt_df_by_stmt_type.iloc[i, 1:].values == '')) and ind != '':
                    prefix = f'{" ".join([index.lower().capitalize() for index in ind.split(" ")])}: '
                elif any(x in ind for x in ['Total', 'Gross']):
                    prefix = ''

                if ind != '':
                    stmt_df_by_stmt_type['index'][i] = f'{prefix}{ind}'

        if stmt_type == 'income/loss/comprehensive_lo':
            empty_rows = [
                i
                for i in range(len(stmt_df_by_stmt_type.index))
                if all(list(stmt_df_by_stmt_type.iloc[i, 1:].values == ''))
            ]
            for i, ind in enumerate(stmt_df_by_stmt_type.iloc[:, 0]):
                if i in empty_rows and ind.split(' ')[0] == 'Other':
                    if ', net' in ind:
                        cleaned_ind = " ".join([
                            i.strip()
                            for i in ind.split(',')[:-1]
                        ]).replace('gain', 'income').replace('incomes', 'income')
                        stmt_df_by_stmt_type['index'][i] = f'{cleaned_ind}: {cleaned_ind}'
                    else:
                        stmt_df_by_stmt_type['index'][i] = f'{ind}: {ind}'
                else:
                    cleaned_ind = ind.replace('gain', 'income').replace('incomes', 'income')
                    stmt_df_by_stmt_type['index'][i] = cleaned_ind
            if not stmt_df_by_stmt_type['index'].is_unique:
                _counter = Counter(stmt_df_by_stmt_type.loc[:, 'index'])
                duplicate_values = [
                    v
                    for v, c
                    in _counter.items()
                    if c > 1 and v != ''
                ]
                all_dup = {
                    dup: stmt_df_by_stmt_type.loc[stmt_df_by_stmt_type['index'] == dup].index.to_list()
                    for dup in duplicate_values
                }
                for _, dup_rows in all_dup.items():
                    for i, dup in enumerate(dup_rows):
                        modified = False
                        for d_ind in range(dup, 0, -1):
                            if not modified:
                                if d_ind in empty_rows and stmt_df_by_stmt_type['index'][d_ind] != '':
                                    stmt_df_by_stmt_type['index'][dup] = f"{stmt_df_by_stmt_type['index'][d_ind]}: {stmt_df_by_stmt_type['index'][dup]}"
                                    modified = True

        if stmt_type == 'flow':
            prefix = ''
            for i, ind in enumerate(stmt_df_by_stmt_type.iloc[:, 0]):
                cleaned_ind = ' '.join([
                    i.strip().capitalize()
                    for i in ind.split(' ')
                ]).replace('Gain', 'Income')
                if ', Net' in cleaned_ind:
                    cleaned_ind = ' '.join(cleaned_ind.split(',')[:-1])
                if all(list(stmt_df_by_stmt_type.iloc[i, 1:].values == '')) and len(ind) < 60:
                    if 'operating activities' in ind.lower():
                        prefix = "CFO: "
                    elif 'investing activities' in ind.lower():
                        prefix = "CFI: "
                    elif 'financing activities' in ind.lower():
                        prefix = "CFF: "
                    elif 'supplimental' in ind.lower():
                        prefix = "Suppl: "

                if stmt_df_by_stmt_type['index'][i] != '':
                    stmt_df_by_stmt_type['index'][i] = f'{prefix}{cleaned_ind}'


        stmt_df_by_stmt_type.set_index('index', inplace=True)
        good_col = [
            i
            for i in range(1, len(stmt_df_by_stmt_type.iloc[0]))
            if (((stmt_df_by_stmt_type.iloc[:, i].values == '').sum()/len(stmt_df_by_stmt_type.iloc[:, i]))*100 <= 40
            and any(x not in stmt_df_by_stmt_type.index.values for x in list(filter(None, stmt_df_by_stmt_type.iloc[:,i])))
            and all(x not in stmt_df_by_stmt_type.iloc[:, i].values for x in ['$', ')']))
        ]
        stmt_df_by_stmt_type = stmt_df_by_stmt_type.iloc[:, good_col]

        bad_rows = [
            n
            for n in range(len(stmt_df_by_stmt_type.index.values))
            if stmt_df_by_stmt_type.index.values[n] == ''
        ]

        good_rows = [
            n
            for n in range(1, len(stmt_df_by_stmt_type.index.values))
            if n not in bad_rows
        ]
        new_header_row = int(good_rows[0])-1

        new_head = [
            ' '.join(re.sub("[\(\[].*?[\)\]/]", "", stmt_df_by_stmt_type.iloc[:new_header_row+1, i].str.cat(sep=' ')).split())
            for i, n in enumerate(stmt_df_by_stmt_type.iloc[new_header_row])
        ]
        stmt_df_by_stmt_type.columns = new_head
        stmt_df_by_stmt_type.iloc[new_header_row] = ''
        stmt_df_by_stmt_type.drop(stmt_df_by_stmt_type.index[bad_rows], inplace=True)
        replacers = {
            '-': 0,
            ',': '',
            '—': '',
            r'\(': '-',
            r'\)': '',
        }
        stmt_df_by_stmt_type.replace(replacers, regex=True, inplace=True)

        for col in stmt_df_by_stmt_type.columns:
            stmt_df_by_stmt_type[col] = pd.to_numeric(stmt_df_by_stmt_type[col], errors='coerce')

        if 'thousand' in scale:
            stmt_df_by_stmt_type = (stmt_df_by_stmt_type/1000).round(2)
        else:
            pass


        stmt_df_by_stmt_type.fillna(0.0, inplace=True)
        return stmt_df_by_stmt_type

    def _find_table_by_type(self, table) -> dict:
        ''' Find tables by statement type. '''
        quarterly_df = {}
        search_params = {
            'p': 'id',
            'a': 'name',
            'span': 'text',
        }
        for stattype in self.stat_types:
            patterns = stattype.split('/')

            found_table = False
            stmt_html = ''
            for k, v in search_params.items():
                for pattern in patterns:
                    if k == 'span':
                        if not found_table:
                            stmt_html = table.find(
                                k,
                                text=re.compile(
                                    pattern.upper(),
                                    re.IGNORECASE,
                                ),
                            )
                        if stmt_html is not None:
                            found_table = True
                    else:
                        if not found_table:
                            stmt_html = table.find(
                                k,
                                {
                                    v: re.compile(
                                        pattern.upper(),
                                        re.IGNORECASE,
                                    )
                                },
                            )
                            if stmt_html is not None:
                                found_table = True

            stmt_df = pd.read_html(
                str(stmt_html.findNext('table')),
                na_values=' ',
                keep_default_na=False,
            )

            try:
                stmt_scale = stmt_html.findNext(
                    'span',
                    text=re.compile(
                        '^\(in',
                        re.IGNORECASE,
                    )
                ).text
            except:
                stmt_scale = stmt_html.findNext(
                    'p',
                    text=re.compile(
                        '^\(in',
                        re.IGNORECASE,
                    )
                ).text
            quarterly_df[stattype] = self._clean_table(
                table=stmt_df[0],
                scale=stmt_scale.split(' ')[1],
                stmt_type=stattype
            )
        return quarterly_df

    def _generate_clean_statements(self, df_data):
        ''' Clean data, transpose, and re-index table. '''
        # Sort the header if the header is a date:
        try:
            new_header = [
                datetime.strptime(
                    header.replace(u'\xa0', u' '),
                    '%B %d,%Y'
                ).date()
                for header in df_data.columns
            ]
            df_data.columns = new_header
        except:
            pass

        df_data = df_data.loc[:, ~df_data.columns.duplicated()].copy()
        df_data = df_data.reindex(sorted(df_data.columns), axis=1)
        t_data_df = df_data.transpose()
        t_data_df.fillna(0.0, inplace=True)

        empty_rows = [
            n
            for n in range(len(t_data_df.index.values))
            if t_data_df.index.values[n] == ''
        ]
        t_data_df.drop(
            t_data_df.index[empty_rows],
            inplace=True,
        )
        return t_data_df

    def generate_all_state_figs(self, all_statements) -> dict:
        ''' Combine all tables of a statement type and return plotted data. '''
        all_results = {
            stype: pd.concat(
                [
                    i[k]
                    for i in all_statements.values()
                    for k in i
                    if stype == k
                ],
                axis=1,
            )
            for stype in self.stat_types
        }

        return {
            stat_type: self._statement_figures(
                all_statements=all_results,
                stat_type=stat_type,
            )
            for stat_type in self.stat_types
        }

    def _statement_figures(
        self,
        all_statements,
        stat_type: str,
    ) -> dict:
        ''' Generate all figures for each type of statement. '''
        fig_data = {}
        if stat_type == 'balance':
            balance_df = self._generate_clean_statements(
                all_statements[stat_type]
            )

            total_balance_stmts = [
                i
                for i, col in enumerate(balance_df, start=1)
                if 'total' in col.lower()
            ]
            total_balance_stmts.insert(0, 0)

            bal_stmt_col = [
                list(
                    balance_df.iloc[
                        :,
                        total_balance_stmts[i]:total_balance_stmts[i+1]
                    ].columns)
                for i in range(len(total_balance_stmts)-1)
            ]

            fig = Figure(figsize=(40, 40))
            for i in range(len(bal_stmt_col)):
                ax = fig.add_subplot(4, 2, i+1)
                ax.plot(
                    balance_df[bal_stmt_col[i][:-1]],
                    '-o',
                    label=bal_stmt_col[i][:-1],
                    linewidth=0.75,
                )
                ax.plot(
                    balance_df[bal_stmt_col[i][-1]],
                    '-o',
                    label=bal_stmt_col[i][-1],
                    linewidth=3,
                )
                ax.legend()

            buf = BytesIO()
            fig.savefig(buf, format="png", bbox_inches='tight')
            fig_data[stat_type] = base64.b64encode(
                buf.getbuffer()
            ).decode("ascii")

        if stat_type in ['income/loss/comprehensive_lo']:
            income_loss_df = self._generate_clean_statements(
                all_statements[stat_type]
            )
            income_loss_df.fillna(0.0, inplace=True)

            totaled_columns = [
                col_name
                for col_name
                in income_loss_df.columns
                if any(name in col_name for name in ['Net income', 'Total other comprehensive', 'Total comprehensive', 'Comprehensive', 'Other comprehensive'])
                and len(col_name) < 50
            ]
            # totaled_columns = ['Net income', 'Total other comprehensive income', 'Total comprehensive income']

            non_empty_col = [
                col
                for col in income_loss_df.columns
                if not all(income_loss_df.loc[:, col].values == 0.0)
                and col not in totaled_columns
            ]

            empty_col = [
                i
                for i in range(len(income_loss_df.iloc[0]))
                if ((income_loss_df.iloc[:, i].values == 0.0).sum()/len(income_loss_df.iloc[:, i])) == 1
            ]
            empty_col.insert(0, -1)
            empty_col.append(len(income_loss_df.iloc[0])-2)

            incstat_col = [totaled_columns, non_empty_col]

            striped_ind2 = [
                parse(dtstr.replace(',', ' '), fuzzy_with_tokens=True)[0]
                if dtstr != '' else ''
                for dtstr in income_loss_df.index
            ]
            income_loss_df['dates'] = striped_ind2

            income_index = {
                i : [ind
                for ind in income_loss_df.index
                if i in ind.lower()]
                for i in ['three', 'six', 'nine']
            }

            fig = Figure(figsize=(20 * len(incstat_col), 50))
            count = 1
            for k in ['three', 'six', 'nine']:
                reduced_df = income_loss_df.loc[income_index[k]]
                ordered_red_df = reduced_df.sort_values(by=['dates'])
                ordered_red_df.set_index('dates', inplace=True)

                for i in range(len(incstat_col)):
                    ax = fig.add_subplot(3, len(incstat_col), count)
                    ax.plot(
                        ordered_red_df[incstat_col[i]],
                        '-o',
                        label=incstat_col[i],
                        linewidth=0.75,
                    )
                    count += 1
                    ax.legend()
                    # ax.set_title(incstat_col[i])

            buf = BytesIO()
            fig.savefig(buf, format="png", bbox_inches='tight')
            fig_data[stat_type] = base64.b64encode(
                buf.getbuffer()
            ).decode("ascii")

        if stat_type == 'flow':
            flow_df = self._generate_clean_statements(
                all_statements[stat_type]
            )
            flow_df.fillna(0.0, inplace=True)

            striped_ind2 = [
                parse(dtstr.replace(',', ' '), fuzzy_with_tokens=True)[0]
                if dtstr != '' else ''
                for dtstr in flow_df.index
            ]
            flow_df['dates'] = striped_ind2

            flow_index = {
                i : [ind
                for ind in flow_df.index
                if i in ind.lower()]
                for i in ['three', 'six', 'nine']
            }
            flow_columns = {
                i : [
                    col
                    for col in flow_df.columns
                    if i in col.lower()
                ]
                for i in ['cfo', 'cfi', 'cfi']
            }
            
            fig = Figure(figsize=(20 * len(flow_columns), 50))
            count = 1
            for k in ['three', 'six', 'nine']:
                reduced_df = income_loss_df.loc[flow_index[k]]
                ordered_red_df = reduced_df.sort_values(by=['dates'])
                ordered_red_df.set_index('dates', inplace=True)

                for i in range(len(flow_columns)):
                    ax = fig.add_subplot(3, len(flow_columns), count)
                    ax.plot(
                        ordered_red_df[flow_columns[i]],
                        '-o',
                        label=flow_columns[i],
                        linewidth=0.75,
                    )
                    count += 1
                    ax.legend()
                    # ax.set_title(flow_columns[i])

            buf = BytesIO()
            fig.savefig(buf, format="png", bbox_inches='tight')
            fig_data[stat_type] = base64.b64encode(
                buf.getbuffer()
            ).decode("ascii")

        return fig_data
