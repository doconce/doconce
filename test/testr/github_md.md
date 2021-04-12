<!-- Test of GitHub Flavored Markdown -->

<!-- Write in doconce -->
<!-- Translate with doconce format pandoc githu_md --github_md -->

> ### Problems with a function
> 
> There is a problem with the `f(x)` function
> 
> 
> ```python
> def f(x):
>     return 1 + x
> ```
> 
> This function should be quadratic.



OK, this is fixed:


```python
def f(x, a=1, b=1, c=1):
    return a*x**2 + b*x + c
```

### Updated task list

   - [x] Offer an `f(x)` function
   - [ ] Extension to cubic functions
   - [x] Allowing general coefficient in the quadratic function

#### Remaining functionality

<table class="table" border="1">
<thead>
<tr><th align="center">function</th> <th align="center">           purpose            </th> <th align="center">      state      </th> </tr>
</thead>
<tbody>
<tr><td align="left">   <code>g(x)</code>      </td> <td align="left">   Compute the Gaussian function.    </td> <td align="left">   Formula ready.       </td> </tr>
<tr><td align="left">   <code>h(x)</code>      </td> <td align="left">   Heaviside function.               </td> <td align="left">   Formula ready.       </td> </tr>
<tr><td align="left">   <code>I(x)</code>      </td> <td align="left">   Indicator function.               </td> <td align="left">   Nothing done yet.    </td> </tr>
</tbody>
</table>

